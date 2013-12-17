# vim: set expandtab:

import random

from pkg.base_exhibit import BaseExhibit

from pkg.general import (
        logger,
        key_down,
        strip_params,
        info,
        Popen,
        )
import os
import subprocess
import time

class Exhibit(BaseExhibit):
    """ Exponat c. 104
        Tlacidla: 'q' (minus), 'w' (plus)
        Svetla: ziadne
        zvuk: generuje sa prikazom, skace sa po frekvenciach, urcenych v 
            nastaveniach
    """

    def __init__(self, invoker,  env, settings):
        BaseExhibit.__init__(self, invoker=invoker, env=env, settings=settings)
        self.tones = self.st.tones
        self.env.game_load.listen_once(self.reset_game)

    @info
    def reset_game(self, data=None):
        BaseExhibit.reset_game(self)
        self.init_game()
        self.sound = None
        self.end_function = None
        self.play_tone()
        self.env.keyboard.find_key(self.st.minus_button).listen(
            strip_params(self.minus_pressed), key_down)
        self.env.keyboard.find_key(self.st.plus_button).listen(
            strip_params(self.plus_pressed), key_down)
    
    @info
    def init_game(self):
        self.tone = len(self.tones)//2

    @info
    def play_tone(self):
        logger.info(str(self.env.finishing_list))
        if self.sound:
            logger.info(str(self.sound))
            self.sound.early_exit()
        logger.info(str(self.st.sound_card_index))
        self.sound = Popen(self.env, ["audio_playing/play_tone.sh",
            str(self.st.sound_card_index), str(self.tones[self.tone])],
            shell=False)
        logger.info(["audio_playing/play_tone.sh",
            str(self.st.sound_card_index), str(self.tones[self.tone])])
        self.seven_print(self.tones[self.tone], "%d")

    @info
    def minus_pressed(self):
        self.tone = max(0, self.tone - 1)
        self.play_tone()

    @info
    def plus_pressed(self):
        self.tone = min(len(self.tones)-1  , self.tone + 1)
        self.play_tone()
        
