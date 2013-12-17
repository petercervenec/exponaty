# vim: set expandtab:

import random
from pkg.general import (
        logger,
        key_down,
        strip_params,
        info,
        )
from pkg.base_exhibit import BaseExhibit
import time

class Exhibit(BaseExhibit):
    @info
    def __init__(self, invoker, env, settings):
        BaseExhibit.__init__(self, invoker=invoker, env=env, settings=settings)
        self.env.game_load.listen_once(self.reset_game)

    @info
    def reset_game(self, qr_register=True):
        BaseExhibit.reset_game(self, qr_register=qr_register)
        self.score = 0
        self.buttons2timers = {}
        self.env.keyboard.listen_once(self.begin_game, key_down)

    @info
    def begin_game(self, key, updown):
        BaseExhibit.begin_game(self)
        self.run_reset_timer(self.reset_game)
        for i in range(5):
            self.change_button()
        self.update_display(self.st.game_time)
        self.env.keyboard.listen(self.process_button_press, key_down)
        self.create_timer(
            self.st.game_time,
            self.st.time_tick_interval,
            callback=self.update_display,
            end_callback=self.time_out).start()

    @info
    def time_out(self):
        now=time.time()
        BaseExhibit.__reset__(self)
        self.seven_flicker(texts=self.score, phormats="%d", lengths=self.env.seven_length, 
            callback=self.reset_game)
        print(time.time()-now)
        self.html('html_score')
        BaseExhibit.end_game(self)

    def update_display(self, t):
        BaseExhibit.update_display(self, t)
        self.seven_print(texts=(t, self.score), phormats=("%.1f", "%d"))

    @info
    def change_button(self, button=None):
        candidates = [l for l in self.env.light_labels if not self.env.lights[l]]
        new_button = random.choice(candidates)
        if button is not None:
            self.env.light(button, 0)
            if button in self.buttons2timers:
                self.buttons2timers[button].cancel()
                del self.buttons2timers[button]
        self.env.light(new_button, 1)
        self.buttons2timers[new_button] = self.create_timer(
            self.st.lighted_button_time(),
            end_callback = lambda: self.change_button(new_button))
        self.buttons2timers[new_button].start()

    @info
    def process_button_press(self, key, updown):
        button = key.label
        if self.env.lights[button]:
            self.score += 1
            self.change_button(button)
        else:
            if not self.score == 0:
                self.score -= 1
        #self.update_display()
