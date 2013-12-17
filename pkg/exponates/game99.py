# vim: set expandtab:

import random
from pkg.general import (
    logger,
    key_down,
    key_up,
    strip_params,
    info,
    )
from pkg.base_exhibit import BaseExhibit
from functools import partial
import time


class Exhibit(BaseExhibit):
    # keyup na start -> zacni ratat cas, pusti timer s casovacom
    # keydown na start -> reset
    # keydown na end -> prestan ratat cas
    # keydown na error -> check ci pred 200 ms nebola uz ina penalta, ak nie,
    # prirataj trestne body
    #                  -> o 200 ms skontroluj stav (keydown? -> dalsie trestne
    #                  body)
    @info
    def __init__(self, invoker, env, settings):
        BaseExhibit.__init__(self, invoker=invoker, env=env, settings=settings)
        self.env.game_load.listen_once(self.reset_game)
        self.is_error = self.env.keyboard.find_key(self.st.error_bl).pressed

    @info
    def reset_game(self, key=None, updown=None):
        BaseExhibit.reset_game(self)
        self.env.keyboard.find_key(self.st.start_bl).listen(strip_params(self.begin_game), key_up)
        self.env.keyboard.find_key(self.st.start_bl).listen(self.reset_game, key_down)
        self.env.keyboard.find_key(self.st.end_bl).listen(strip_params(self.end_game), key_down)
        self.env.keyboard.find_key(self.st.error_bl).listen(self.error_down, key_down)
        self.env.keyboard.find_key(self.st.error_bl).listen(self.error_up, key_up)

        self.penalty_timer = None
        self.infinite_timer = None
        self.playing = False
        self.score = 0
        self.penalty_count = 0
        self.last_penalty = -2*self.st.penalty_timeout

        if not self.is_qr_registered:
            self.qr_register()

    def error_up(self, key=None, updown=None):
        self.is_error = False
        self.env.light(self.st.error_ll, 0)

    @info
    def begin_game(self):
        try:
            BaseExhibit.begin_game(self)
        except:
            pass
        self.playing = True
        self.start_time = time.time()
        self.start_infinite_timer()
        if self.is_error:
            self.error_move(1)

    @info
    def start_infinite_timer(self):
        self.infinite_timer = self.create_timer(60, self.st.time_tick_interval,
            callback=strip_params(self.check_and_print_score),
            end_callback=self.start_infinite_timer)
        self.infinite_timer.start()

    def check_and_print_score(self):
        if self.count_score()>=1000:
            self.reset_game()
        else:
            self.seven_print(texts=self.count_score(), phormats="%.1f")

    def error_down(self, key=None, updown=None):
        self.is_error = True
        self.env.light(self.st.error_ll, 1)
        if time.time() - self.last_penalty < self.st.penalty_timeout:
            return
        self.error_move(1)

    @info
    def error_move(self, penalty_multiple):
        if self.is_error:
            self.last_penalty = time.time()
            self.penalty_count += penalty_multiple
            self.penalty_timer = self.create_timer(
                self.st.penalty_timeout,
                end_callback=lambda: self.error_move(self.st.second_penalty_multiple))
            self.penalty_timer.start()

    @info
    def end_game(self):
        if not self.playing:
            return
        self.playing = False
        if self.infinite_timer is not None:
            self.infinite_timer.cancel()
        self.count_score()
        self.seven_flicker(texts=self.count_score(), phormats="%.1f",
                           end_text='---', callback=self.reset_game)
        BaseExhibit.end_game(self)

    def count_score(self):
        _time = time.time() - self.start_time
        penalty = self.st.penalty * self.penalty_count
        score = _time + penalty
        self.score = score
        return score
