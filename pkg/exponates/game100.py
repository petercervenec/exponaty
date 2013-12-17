# vim: set expandtab:

from ..general import (
        logger,
        key_down,
        strip_params,
        info,
        )
from pkg.base_exhibit import BaseExhibit

import os

import time

class Exhibit(BaseExhibit):
    """ Exponat c. 100
        Tlacidlo: 'a'
        Svetla: ziadne
    """

    @info
    def __init__(self, invoker, env, settings):
        #call of super-class __init__
        BaseExhibit.__init__(self, invoker=invoker, env=env, settings=settings)
        #when game_load even fires, reset_game is invoked. This happens just once
        self.env.game_load.listen_once(self.reset_game)

    @info
    def reset_game(self, data=None, qr_register=True):
        #super-class call
        BaseExhibit.reset_game(self, qr_register=qr_register)
        self.init_game()
        #listen once for (any) keyboard event, invoke begin_game when it occurs. Any arguments that
        #are passed to begin_game are stripped by strip_params decorator
        self.env.keyboard.listen_once(strip_params(self.begin_game))
    
    def init_game(self):
        #set score and remaining time to their initial values
        self.time=self.st.game_time
        self.score = 0

    @info
    def begin_game(self):
        #super-class call
        BaseExhibit.begin_game(self)
        #listen to keyboard events, filter key_down events, invoke pressed_button function when
        #key_down event occurs
        self.env.keyboard.listen(self.pressed_button, key_down)
        #create timer that will periodically tick and invoke corresponding callbacks at each tick an
        #at the end of the process
        self.create_timer(self.st.game_time, self.st.time_tick_interval, 
            callback=self.time_tick, end_callback=self.time_out).start()
        #see superclass for documentation
        self.run_reset_timer(self.reset_game)

    def time_tick(self, time):
        self.time = time
        self.update_display(time)

    @info
    def time_out(self):
        #reset game
        self.__reset__()
        self.end_game()
        #when flickering ends, call reset_game
        self.seven_flicker(texts=self.score, phormats="%d", 
            lengths=self.env.seven_length, callback=self.reset_game, 
            end_text='---')

    def update_display(self,t):
        BaseExhibit.update_display(self,t)
        self.seven_print(texts=(self.time, self.score), phormats=("%.1f","%d"))

    def pressed_button(self, key, updown):
        self.score += 1

