import random

from pkg.general import (
        logger,
        key_down,
        key_up,
        strip_params,
        info,
        )

import time
from pkg.base_exhibit import BaseExhibit

class Exhibit(BaseExhibit):
    """
    testing exhibit
    """
    def __init__(self, invoker,  env, settings):
        BaseExhibit.__init__(self, invoker=invoker, env=env, settings=settings)
        self.env.game_load.listen_once(self.reset_game)
        self.env.game_load.listen_once(self.qr_register)

    @info
    def reset_game(self, qr_register=False):
        BaseExhibit.reset_game(self, qr_register=qr_register)
        self.light(0)
        self.score = 0
        self.seven_print(texts=self.score%1000, phormats='%d')
        self.html('html_instr')
        self.env.keyboard.listen(self.action_down, key_down)
        self.env.keyboard.listen(strip_params(self.action_up), key_up)

    def action_down(self, key, updown):
        button_num = self.st.key_map.keys().index(key.label)
        light_count = len(self.st.light_map.keys())
        if light_count is not 0:
            light_num = button_num % light_count+1
            self.light(0)
            for label in self.st.light_map.keys():
                self.env.light(label, 1)
                time.sleep(0.05)
            self.light(0)
            self.light(1, light_num)
            self.score += light_num
        else:
            self.score += 1
        self.seven_print(texts=self.score % 1000, phormats='%d')
        self.html('html_score')
    
    def action_up(self):
        self.light(0)

    def light(self, updown=0, count=None):
        if count == None:
            count = len(self.st.light_map.keys())
        for label in self.st.light_map.keys():
            self.env.light(label, updown)
            count -= 1
            if count == 0: break
