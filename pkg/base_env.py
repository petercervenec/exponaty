# vim: set expandtab:

from pkg.general import (
        logger,
        strip_params,
        Key,
        Keyboard,
        QrScanner,
        EventProducer,
        info
        )
import threading
import os
import gtk 
import webkit 
import time
import gobject as gob
import httplib
import json
from collections import OrderedDict, deque
from subprocess import Popen, PIPE
from pkg.general import info
import alsaaudio


class SoundWorker:
    """
    see ``SoundExecutor``
    """
    def __init__(self, executor, samples, settings):
       self.sound_name=None
       self.executor=executor
       self.samples=samples
       self.st = settings
       self.cond=threading.Condition()
       self.end=False
       self.thread=threading.Thread(target=self.run)
       self.thread.start()

    @info
    def run(self):
        while not self.end:
            self.play_process = Popen(["aplay", "-D","plughw:" +
                str(self.st.sound_card_index) + ",0"], stdin=PIPE)
            with self.cond:
                while not self.sound_name and not self.end:
                    self.cond.wait()
            if not self.end:
                if not self.sound_name.endswith('.wav'):
                    self.sound_name+='.wav'
                sound_stream=self.samples[self.sound_name]
                self.play_process.communicate(sound_stream)
                self.sound_name=None
                self.executor.run()

    @info
    def __exit__(self):
        self.end=True
        with self.cond:
            self.cond.notify_all()

class SoundExecutor:
    """
    main class for dealing with sounds, SoundExecutor instance creates several SoundWorker
    instances, each one opening new ``aplay`` process and piping sound data into it as soon as the
    playing sound is needed. 

    However, because of raspbian-alsa bug that causes system to freeze when playing several sounds
    at once or even two sounds rather shortly one after another, we use one-soundworker-mode (see
    settings) in which only one soundworker exists.
    """

    def __init__(self, samples, settings=None):
        self.st = settings
        self.cond=threading.Condition()
        self.workers=[SoundWorker(self, samples, self.st) for i in range(settings.sound_worker_count)]
        self.commands=deque()

        
    def run(self):
        with self.cond:
            free_workers=[worker for worker in self.workers if not worker.sound_name]
            if self.commands and free_workers:
                worker=free_workers[0]
                sound_name=self.commands.popleft()
                with worker.cond:
                    worker.sound_name=sound_name
                    worker.cond.notify()

    @info
    def play_sound(self, sound_name):
        """
        plays given sound using first available sound worker 
        """
        #if functioning in one_sound_worker_mode, force its availability by killing the underlying
        #play process
        if hasattr(self.st, 'one_sound_worker_mode') and self.st.one_sound_worker_mode:
            worker=self.workers[0]
            self.commands.clear()
            with worker.cond:
                if worker.sound_name!=None:
                    try:
                        worker.play_process.kill()
                        worker.play_process.wait()
                        time.sleep(0.2)
                    except Exception:
                        pass
        with self.cond:
            self.commands.append(sound_name)
            self.run()

    def __enter__():
        pass

    @info
    def __exit__(self):
        for worker in self.workers:
            worker.__exit__()

class BaseEnv:
    """
    common abstract parent of all environments

    properties that need to be supplied by real environment:
        keyboard - Keyboard object
        lights - {label: state} ordered dict
        light(label, state) - set light with label 'label' to state 'state' (0 or 1)
        _seven_print(text) - prints text on the 7-segment-display
        
    """

    def __init__(self, invoker, settings=None):
        """
        `invoker` - same as exhibit's invoker
        `key_map` - maps logical key label to physical adress (i.e. keyboard button or expander pin adress)
        `light_map` - maps logical light labels to physical adress (similar to key_map)
        `snd_path` - root path to sound samplse
        `seven_length` - length of seven-segment display, may not be set if exhibit does not have one
        """

        # clean up - kill all processes that shouldn't be running - maybe they weren't closed
        # properly during the last run
        kia = ['barcode', 'zbarcam', 'vol_pipe','arecord', 'play_tone',
            'aplay', 'play', 'picocom']
        for k in kia:
            try:
                os.system("pkill --signal CONT " + k)
            except:
                pass
            try:
                os.system("pkill --signal KILL "+ k)
            except:
                pass

        self.st=settings
        self.invoker=invoker
        self.key_map=settings.key_map
        self.light_map=settings.light_map
        self.keyboard = Keyboard(invoker, settings.key_map)
        self.seven_length=settings.seven_length
        self.light_labels=list(settings.light_map.keys())
        self.lights=OrderedDict((label, 0) for label in self.light_labels)
        self.snd_path=settings.snd_path
        self.finishing_list = []
        self.qr=self.st.qr_factory(invoker, settings, self)
        self.qr.start()
        self.game_load=EventProducer(invoker)
        try:
            os.system("./audio_playing/force_analogue_audio.sh")
        except Exception as e:
            logger.error("forec_analog" + str(e))
        if self.st.enable_soundworker:
            self.samples={}
            sample_file_names=[os.path.join(root, filename) for root, dirnames, filenames in
                    os.walk(self.snd_path) if dirnames==[] for filename in filenames]
            for filename in sample_file_names:
                with open(filename) as fyle:
                    self.samples[os.path.relpath(filename, self.snd_path)]=fyle.read()
        logger.info("setting sound devices by pyalsaaudio")
        try:
            card = self.st.sound_card
            card_control = self.st.sound_card_control
            if not (card in alsaaudio.cards()):
                logger.error("sound card %s not found "%card)
                logger.error(str(alsaaudio.cards()))
            else:
                self.st.sound_card_index = alsaaudio.cards().index(card)
                mixer = alsaaudio.Mixer(cardindex=self.st.sound_card_index, control=card_control)
                mixer.setvolume(self.st.volume)
                mixer = alsaaudio.Mixer(cardindex=self.st.sound_card_index,
                        control=self.st.sound_card_control_mic)
                mixer.setvolume(self.st.record_sensitivity, 0, "capture")
                mixer.setvolume(self.st.record_sensitivity, 1, "capture")
        except Exception as e:
           logger.error(e)
        logger.info("setting sound devices is finished.")
        
        if self.st.enable_soundworker:
            self.sound_executor=SoundExecutor(self.samples, self.st)
        



    @info
    def play_sound(self, name):
        """
        Plays the sound with the given `name`. 
        `name` - relative path to the sound file with respect to snd_path setting
        """
        self.sound_executor.play_sound(name)

    
    def start_gtk_thread(self):
        """
        starts gtk thread responsible for managing screen output of an exhibit; if everything is ok,
        screen shows hello world message
        """
        threading.Thread(target = gtk.main).start()
        def update():
            view = webkit.WebView() 
            self.html_view=view
            sw = gtk.ScrolledWindow() 
            sw.add(view) 
            win = gtk.Window(gtk.WINDOW_TOPLEVEL) 
            win.add(sw) 
            win.show_all() 
            self.main_window=win
            self.main_window.fullscreen()
            view.load_html_string('''
                    <html> 
                    <head>
                    </head>
                    <body>
                    <h1> 
                    hello world!
                    </h1> 
                    </html> 
                    ''', 'file:///pokus.py' )
        gob.idle_add(update)

    def print_html(self, html):
        """
        schedules given html string to be displayed in the gtk thread
        """
        logger.debug('html: %s'%html)
        def _print():
            self.html_view.load_html_string(html, 'file:///pokus.py')
        gob.idle_add(_print)


    def ignore_if_set(fn):
        """
        decorator that causes function to ignore communication with server if ``ignore_server`` setting is set to True
        """
        def res(self, *args, **kwargs):
            if self.st.ignore_server:
                logger.info('ignoring communication with server %s'%str(fn.__name__))
            else:
                return fn(self, *args, **kwargs)
        return res

    @ignore_if_set
    def get_user_info(self, user_id, callback=None, timeout=0.5):
        """Returns dict with data about user (name, age, gender, location). 
        """
        address, port = self.st.server_url()
        try:
            conn = httplib.HTTPConnection(address, port, timeout=timeout)
            conn.request('GET', '/get-user-info/%d/' % (user_id,))

            res = conn.getresponse()
            if res.status != 200:
                logger.error('Server response is not 200 OK: %s'%str(res) + str(res.status) + ' ' + str(res.reason))
                conn.close()
            else:
                data = json.loads(res.read())
                conn.close()
                if 'error' in data:
                    logger.error(data['error'])
                else:
                    if callback is not None:
                        callback()
                    return data       
        except Exception as e:
            logger.error(str(e))
            return {'error':str(e)}

    @ignore_if_set
    def get_max_score(self, exponat_name, exponat_level, callback=None, timeout=0.5):
        """Returns best daily score. If none exists, returns None.
        """
        exponat_name = str(exponat_name)
        exponat_level = str(exponat_level)
        address, port = self.st.server_url()
        try:
            conn = httplib.HTTPConnection(address, port, timeout=timeout)
            logger.info(exponat_name + ',' + exponat_level)
            conn.request('GET', '/get-max-score/%s/%s/' % (exponat_name, 
                exponat_level,))

            res = conn.getresponse()
            if res.status != 200:
                logger.error('Server response is not 200 OK: %s'%str(res) + 
                    str(res.status) + ' ' + str(res.reason))
                conn.close()
            else:
                text = res.read()
                logger.info(text)
                data = json.loads(text)
                conn.close()
                if 'error' in data:
                    logger.error(data['error'])
                else:
                    if callback is not None:
                        callback()
                    return data['max_score']
        except Exception as e:
            logger.error(str(e))

    @ignore_if_set
    def upload_game_results(self, exponat_name, user_id, score=None, level=None, 
        additional_data=None, callback=None, timeout=0.5):
        """Uploads data about game to server. ``additional_data`` can be arbitrary piece of data (in
        a dict form) that is attached to the result and its pickled form is stored in the database.
        """
        logger.info('upload_game_results')
        address, port = self.st.server_url()
        try:
            conn = httplib.HTTPConnection(address, port, timeout=timeout)
            conn.request('POST', '/upload-game-results/', json.dumps({
                'exponat_name':exponat_name, 'user_id':user_id, 'score':score,
                'level':level, 'additional_data':additional_data}))

            res = conn.getresponse()
            if res.status != 200:# vim: set expandtab:


                logger.error('Server response is not 200 OK: %s'%str(res) + 
                    str(res.status) + ' ' + str(res.reason))
                conn.close()
            else:
                data = json.loads(res.read())
                conn.close()
                if 'error' in data:
                    logger.error(data['error'])
                else:
                    if callback is not None:
                        callback()
        except Exception as e:
            logger.error(str(e))

    def __exit__(self):
        """
        exits the whole environment; trying to do it properly althought some corner-cases are still
        not-properly-handled
        """
        if hasattr(self, 'sound_executor'):
            self.sound_executor.__exit__()
        self.finishing_list.append(lambda: os.system("pkill zbarcam"))
        for i in self.finishing_list:
           try:
                if hasattr(i, '__call__'): i()
           except Exception as e:
                logger.error(e)
