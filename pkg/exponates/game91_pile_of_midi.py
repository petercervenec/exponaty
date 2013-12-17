# vim: set expandtab:

import random
import os
import threading

from pkg.general import (
        key_down,
        key_up,
        strip_params,
        info,
        logger
        )

from pkg.base_exhibit import BaseExhibit

import alsaseq
import time
from alsamidi import noteonevent, noteoffevent


class Exhibit(BaseExhibit):
    """ Exponat c. 91 - klavir
    """

    @info
    def __init__(self, invoker, env, settings):
        BaseExhibit.__init__(self, invoker, env, settings)
        self.env.game_load.listen_once(self.reset_game)
        self.env.game_load.listen_once(self.qr_register)
        try:
            logger.info(os.system("pgrep timidity"))
            logger.info(os.system("pkill timidity"))
            logger.info(os.system("timidity -iA -Os -B5,12 &"))
            #logger.info(os.system("timidity -iA -Os"))
            time.sleep(2) #essential for good connection
            alsaseq.client( 'Simple', 1, 1, True )
            alsaseq.connectto( 1, 128, 0 )

            alsaseq.start()
            logger.info("timidity is ok. (i hope)")
        except Exception as e:
                logger.error("timidity" + str(e))

        self.st.max_tone_amount = 3
        self.tones_playing = []

    @info
    def reset_game(self, data=None):
        BaseExhibit.reset_game(self)
        self.init_game()
        self.begin_game()

    def set_score(self, score):
        self.score=score
        self.seven_print_str(str(score))

    @info
    def init_game(self):
        '''tones=[20+i*self.st.span for i in range(16)]
        self.max_tone = max(tones)
        self.min_tone = min(tones)
        tones=[("tones/{color}/{num}".format(color=self.st.get_color(), num=num), num) for num in tones]
        '''

        self.st.base = 35
        tones = [self.st.base + i for i in range(16)]
        self.max_tone = max(tones)
        self.min_tone = min(tones)

        tones = [(i,i) for i in tones]
        
        #random.shuffle(tones)
        tone_keys=[key for key in self.env.keyboard.keys if key.label not in ['reset', 'submit']]
        if len(tones)!=len(tone_keys):
            raise Exception
        self.tone_map={key:tone for key,tone in zip(tone_keys, tones)}
        self.submit=False
        self.set_score(0)
        #self.tones_amount = 0

    @info
    def begin_game(self):
        #BaseExhibit.begin_game(self) vypnute kvoli qr_unregister()
        self.env.keyboard.listen(self.button_down, key_down)
        self.env.keyboard.listen(self.button_up, key_up)

    @info 
    def midi_play_tone(self, x):
        if len(self.tones_playing) < self.st.max_tone_amount:
            alsaseq.output(noteonevent(1, x, 120))
            self.tones_playing.append(x)
    @info
    def midi_stop_tone(self, x):
        if x in self.tones_playing:
            alsaseq.output(noteoffevent(1, x, 120))
            self.tones_playing.remove(x)
    
    @info
    def midi_success_accord(self):
        _akord = [0, 12]
        akord = [self.st.base + 40 + x for x in _akord]
        for t in akord:
            alsaseq.output(noteonevent(1, t, 120))
        logger.info("midi_success, 1.faza")
        time.sleep(2)

        for t in akord:
            try:
                alsaseq.output(noteoffevent(1, t, 120))
            except Exception as e:
                logger.error("midi_success: " + str(e))
        logger.info("midi_success, posledna faza")
    
    @info
    def midi_success(self):
        try:
            os.system("timidity " + self.st.midi_success_file)
        except Exception as e:
            logger.error("midi_success " + str(e))


    @info
    def midi_failure(self):
        try:
            os.system("timidity " + self.st.midi_failure_file)
        except Exception as e:
            logger.error("midi_failure " + str(e))

    @info
    def midi_failure_accord(self):
        _akord = [0,3,6]
        akord = [self.st.base - 12 + x for x in _akord]
        for t in akord:
            alsaseq.output(noteonevent(1, t, 120))
        time.sleep(2)

        for t in akord:
            alsaseq.output(noteoffevent(1, t, 120))



    @info
    def button_down(self, key, updown):
        if key.label == 'reset':
            self.reset_game()
        elif key.label == 'submit':
            self.submit=True
        else:
            self.set_score(self.score+1)
            sound,num=self.tone_map[key]
            if self.submit:
                self.submit=False
                if num==self.max_tone:
                    #self.env.play_sound('global/applause')
                    self.midi_success()
                    self.end_game()
                else:
                    #self.env.play_sound('global/fail')
                    self.midi_failure()
                    self.set_score(self.score+3)
            else:
                self.midi_play_tone(sound)
    
    @info
    def button_up(self, key, updown):
        if key.label == "submit" or key.label == "reset":
            return
        sound, num = self.tone_map[key]
        self.midi_stop_tone(sound)

    @info
    def end_game(self):
        BaseExhibit.__reset__(self)
        #BaseExhibit.end_game(self)
        logger.info(str(self.user_id))
        self.env.upload_game_results(exponat_name=self.st.exhibit.name, 
            user_id=self.user_id, score=self.score, level=self.st.level.name, 
            timeout=10)
        self.html('html_score')
        ## end of BaseExhibit.end_game(self)
        self.seven_flicker(self.score, "%d", callback=self.reset_game)

