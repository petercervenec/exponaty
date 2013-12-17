from pkg.general import (
       logger,
       Timer,
       strip_params,
       info,
       )
from functools import partial
import re
import subprocess
import os
import pkg
from pkg.emulator import Emulator

import time

def empty_callback(*args, **kwargs):
    pass

class BaseExhibit:
    """
    base class for all exhibits
    """
    @info
    def __init__(self, invoker=None, env=None, settings=None):
        self._reset_timer = None
        self.env=env
        self.invoker=invoker
        self.timers=[]
        self.sound_timer = None
        self.st=settings
        self.user=None
        self.user_id=None
        self.max_score=None
        self.is_qr_registered = False
        if self.env.seven_length:
            self.default_seven_text = "-"*self.env.seven_length
        self.env.game_load.listen_once(self.update_max_score)
        if self.env.__class__==Emulator:
            self.env.qr_textbox.set_text('qr ########') 
        
    def create_timer(self, total, interval=None, callback=empty_callback, end_callback=empty_callback, user_data=None):
        """Returns the general.Timer() instance.

        Timer calls `callback` every `interval` seconds for `total` seconds from begining. Finally,
        `end_callback` gets called with the given `user_data` object as the only argument. The
        calls for `callback` are supplied with number of seconds left as a first parameter and
        `user_data` object as the second argument.
        """
        def is_function(fn):
            return hasattr(fn, '__call__') 
        if not(is_function(callback)) or not(is_function(end_callback)):
            raise Exception("callback cannot be None anymore. You have no power were!!!!")
        timer = Timer(self.invoker, total, interval=interval, callback=callback,
                end_callback=end_callback, user_data=user_data)
        self.timers.append(timer)
        return timer

    def run_reset_timer(self, reset_callback, _time=None):
        """
        use Timer implementation to reset game after `time` seconds of inactivity. After this time,
        reset_callback is invoked.
        """
        if _time is None:
            _time=self.st.default_reset_time
        self.activity_timer=None
        def ecb(self):
            self.stop_reset_timer()
            reset_callback()
        def reset():
            if self.activity_timer != 'cancelled':
                if self.activity_timer:
                    self.activity_timer.cancel()
                self.activity_timer=self.create_timer(_time, end_callback=partial(ecb, self))
                self.activity_timer.start()
        self.activity_keypress_cb=self.env.keyboard.listen(strip_params(reset))
        reset()

    def stop_reset_timer(self):
        self.env.keyboard.remove_callback(self.activity_keypress_cb)
        self.activity_timer.cancel()
        self.activity_timer='cancelled'

    @info
    def qr_register(self):
        """
        wake zbarcam process, let it generates outputs from webcam and listen to such events 
        """
        if not self.is_qr_registered:
            os.system("pkill --signal CONT zbarcam")
            self.qr_callback=self.env.qr.listen(self.process_qr)
            self.is_qr_registered = True
            if self.env.__class__==Emulator:
                self.env.qr_textbox.set_text('qr on')

    @info
    def process_qr(self, qr_string):
        """
        function that processes qr event; it:
          1) parses the string obtained from zbarcam
          2) shows appropriate screen (html_welcome / html_bye)
          3) after qr_instr_time (see settings), calls reset_game
        """
        self.__reset__()
        user_id=int(qr_string.split('=')[1])
        if self.user_id is None or self.user_id != user_id:
            self.user_id=user_id
            self.user=self.env.get_user_info(user_id, timeout=self.st.url_timeout)
            if self.user is None or 'error' in self.user:
                self.user = None
            self.html('html_welcome')
        elif user_id == self.user_id:
            self.user_id = None
            self.user = None
            self.html('html_bye')
        self.create_timer(self.st.qr_instr_time, end_callback=self.reset_game).start()

    @info
    def qr_unregister(self):
        """
        stop zbarcam process and stop responding to zbarcam events (this shouldn't be necessary)
        """
        if self.is_qr_registered:
            os.system("pkill --signal STOP zbarcam")
            self.env.qr.remove_callback(self.qr_callback)
            self.is_qr_registered = False
            if self.env.__class__==Emulator:
                self.env.qr_textbox.set_text('qr off')

    @info
    def get_user_name(self):
        return self.user['fullname'] if self.user and 'fullname' in self.user else ""

    @info
    def update_max_score(self):
        """
        helper function that uses env.get_max_score to obtain max score and then attaches it to the
        self object
        """
        res = self.env.get_max_score(exponat_name=self.st.exhibit.name, 
            exponat_level=self.st.level.name, timeout=self.st.url_timeout)
        if isinstance(res, float):
            self.max_score = self.st.max_score_format % (res,)

    @info
    def get_max_score(self):
        try:
            return self.max_score
        except Exception:
            return ''

    @info
    def seven_flicker(self, texts, phormats=None, lengths=None, callback=None, end_text=None):
        """
        flicker text on seven-segment display. Total time and interval of the flicking are taken
        from exhibit settings, `texts`, `phormats` and `lengths` are passed to seven_print function.
        `callback` to execute after flicking ends
        `end_text` final text to show after flickering.
        """
        if end_text is None:
            end_text=self.default_seven_text
        visible={'val': True}
        def ecb(*args):
            self.seven_print_str(end_text)
            if callback: callback()
        def cb(*args):
            if visible['val']:
                self.seven_print(texts=texts, phormats=phormats, lengths=lengths)
            else:
                self.seven_print_str('')
            visible['val']=not visible['val']
        timer = self.create_timer(total=self.st.flicker_time, interval=self.st.flicker_interval, callback=cb, end_callback=ecb)
        timer.start()
        return timer

    @info
    def html(self, screen, **additional):
        self.env.print_html(self.st.decorate_html(getattr(self.st, screen)(self, **additional)))

    def update_display(self, t):
        self.html('html_info', time=t)

    @info
    def begin_game(self):
        self.qr_unregister()

    def __format__(self, text, phormat, length):
        """
        helper text-formatting function
        """
        text = phormat%text
        _text = re.sub(r'[.,]','',text)
        while len(_text)>length:
            text=text[0:-1]
            _text = re.sub(r'[.,]','',text)
            logger.warn('stripping 7 segment text too long; stripping it')
        text=' '*(length-len(_text))+text
        return text

    def seven_print(self, texts, phormats, lengths=None):
        """
        seven-segment-display print couple of texts formatted in the given formats and padded up to
        given lengths. Handles text phormating, then uses env._seven_print as a core environment printing function
        `texts` - tuple of texts to print
        `phormats` - tuple of formats such as "%.1f"
        `lengths` - tuple of lengths
        if any parameter from above is 1-tuple such as (x,), plain x can be passed instead of it
        if lengths of the parameters are inconsistent, Exception is raised.
        """
        if type(texts)!=tuple:
            texts=(texts,)
        if type(phormats)!=tuple:
            phormats=(phormats,)
        if lengths is None:
            try:
                lengths=self.st.seven_lengths
            except Exception:
                if len(texts)==1:
                    lengths=(self.env.seven_length,) 
                else:
                    raise(Exception('lengths for seven_print not cannot be deduced!'))
        if type(lengths)!=tuple:
            lengths=(lengths,)
        if len(texts)!=len(phormats) or len(phormats)!=len(lengths):
            raise Exception('inconsistent lengths of parameters passed to seven_print')
        text="".join(self.__format__(text, phormat, length) for text, phormat, length in zip(texts,
            phormats, lengths))
        self.env._seven_print(text)

    def seven_print_str(self, text):
        """
        partial of seven_print; prints one string padded to the whole lengths of the display
        """
        self.seven_print(texts=(text,), phormats=("%s",), lengths=self.env.seven_length)


    def reset_lights(self):
        """Turn off all lights.
        """
        for label in self.env.light_labels:
            self.env.light(label, 0)

    @info
    def end_game(self):
        """
        default end_game, i.e.: uploads game results, get max score from the server (this could
        change because of update) and show appropriate html screen
        """
        logger.info(str(self.user_id))
        self.env.upload_game_results(exponat_name=self.st.exhibit.name, user_id=self.user_id, score=self.score, level=self.st.level.name, timeout=self.st.url_timeout)
        self.update_max_score()
        self.html('html_score')

    @info
    def reset_game(self, reset_seven=True, qr_register=False):
        self.__reset__()
        self.html('html_instr')
        if qr_register:
            self.qr_register()
        if reset_seven:
            if self.env.seven_length:
                self.seven_print_str(self.default_seven_text)

    @info
    def __reset__(self):
        """ Resets lights, clears the 7digit display, stops any sound playing,
            disconnets all event handlers and cancel all pending timeouts
        """
        self.env.invoker.commands.clear()

        # Foremost, cancel the timers to prevent race conditions.
        for timer in self.timers:
            timer.cancel()
        del self.timers[:]

        self.env.game_load.remove_callbacks()
        self.env.keyboard.remove_callbacks()
        for key in self.env.keyboard.keys:
            key.remove_callbacks()

        self.reset_lights()
