# vim: set expandtab:

import random

from pkg.base_exhibit import BaseExhibit

from pkg.general import (
        logger,
        key_down,
        strip_params,
        info,
        Invoker,
        Popen,
        EventProducer,
        )

import logging

import os

import os

from time import (
        time,
        sleep
        )

from threading import (
        Thread,
        )

import sys
#import os
import re
import subprocess
import wave
import base64


class VolumeLevel(EventProducer):
    def __init__(self, invoker, settings, env, callback=None, end_callback=None,
            recorder=None):
        EventProducer.__init__(self, invoker)
        self.callback = callback
        self.end_callback = end_callback
        self.st = settings
        self.env = env
        self.recorder = recorder

    @info
    def start(self):
        @info
        def _start():
            logger.info(self.st.script_command)
            with Popen(self.env, [self.st.script_command, str(self.st.sound_card_index)], shell=False, 
                    stdout=subprocess.PIPE) as child:
                if not(self.recorder is None): self.recorder.start()
                while True:
                    out = child.stdout.read(150)
                    if out == '' and child.poll() != None:
                        break
                    reg = r'(\d{1,3})\%'
                    ans = re.findall(reg, out)
                    if len(ans) != 0:
                        try:
                            self.fire_event(int(ans[0]))
                        except Exception as e:
                            logger.error(e)
        t = Thread(target=_start)
        t.daemon = True
        t.start()


class AudioRecord(EventProducer):
    def __init__(self, invoker, settings, callback=None, end_callback=None):
        EventProducer.__init__(self, invoker)
        self.callback = callback
        self.end_callback = end_callback
        self.st = settings
    
    @info
    def start(self):
        def _start():
            try:
                logger.info('waiting while sound pipe is created')
                sleep(4)
                f = open(self.st.pipe_source, 'rb')
                buffer = []
                sizebuf=0
                while True:
                    out = f.read(2000)
                    if len(out)>0:
                        logger.info("chunk length: " + str(len(out)))
                        buffer.append(out)
                        sizebuf+=len(out)
                        if sizebuf > self.st.buffer_size:
                            sizebuf=0
                            self.fire_event(''.join(buffer))
                            buffer = []
            except Exception as e:
                logger.error(e)
        t = Thread(target=_start)
        t.daemon = True
        t.start()


class Exhibit(BaseExhibit):
    @info
    def __init__(self, invoker,  env, settings):
        BaseExhibit.__init__(self, invoker=invoker, env=env, settings=settings)
        logger.info("hura, BaseExhibit.__init__ skoncil.")
        self.env.game_load.listen_once(self.mega_reset_game)

    @info
    def mega_reset_game(self):
        self.audio_record = AudioRecord(self.invoker, settings=self.st)
        self.volume_level = VolumeLevel(self.invoker, settings=self.st,
                env=self.env, recorder=self.audio_record)
        self.reset_game()
        self.qr_register()
        self.volume_level.start()
        self.volume_level.listen(self.caser)
        self.audio_record.listen(self.recorder)
        self.mute = False

    @info
    def reset_game(self):
        BaseExhibit.reset_game(self)
        self.init_game()

    @info
    def init_game(self):
        self.idle = True
        self.record = b''
        self.score = 0
        self.timer = None

    @info
    def begin_game(self):
        try:
            BaseExhibit.begin_game(self)
        except Exception as e:
            logger.error(e)
        self.idle = False

    @info
    def end_game(self):
        self.mute = True
        self.idle = True
        self.timer = None
        #BaseExhibit.end_game(self)
        logger.info("dlzka wav: "+str(len(self.make_wav(self.record))))
        self.env.upload_game_results(exponat_name=self.st.exhibit.name, 
            user_id=self.user_id, score=self.score, level=self.st.level.name, 
            timeout=self.st.url_timeout, additional_data={
                'record':base64.b64encode(self.make_wav(self.record)),
            })
        #end of BaseExhibit.end_game(self)
        self.update_max_score()
        self.reset_game()
        self.qr_register()
        self.mute = False

    def make_wav(self, record):
        waf = wave.open("tmp/scream.wav", 'wb')
        waf.setparams((1, 2, 16000, 16000*4, 'NONE', 'noncompressed'))
        waf.writeframes(record)
        waf.close()
        f = open("tmp/scream.wav", 'rb')
        res = f.read()
        f.close()
        return res


    @info
    def caser(self, volume):
        if self.mute: return

        if self.idle and volume <= self.st.threshold:
            pass
        elif self.idle and volume > self.st.threshold:
            self.begin_game()
            act_score=int((volume-self.st.threshold)*1000)
            self.score = max(self.score, act_score)
            self.html('html_score')
            self.seven_print(self.score, '%d')
        elif (not self.idle) and volume > self.st.threshold:
            if self.timer:
                self.timer.cancel()
                self.timer = None
            self.score = max(self.score, volume)
            self.html('html_score')
            self.seven_print(self.score, '%d')
        elif (not self.idle) and volume <= self.st.threshold:
            if self.timer:
                pass
            else:
                self.timer = self.seven_flicker(self.score, phormats='%d', 
                    callback=self.end_game)

    # no @info, because of 5MB string in sample
    def recorder(self, sample):
        logger.info('recorder, idle=' + str(self.idle))
        if self.idle:
            pass
        else:
            self.record += sample
