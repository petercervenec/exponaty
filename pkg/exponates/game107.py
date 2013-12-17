# vim: set expandtab:

import random

from pkg.base_exhibit import BaseExhibit

from pkg.general import (
        logger,
        key_down,
        strip_params,
        info,
        )

import logging

class Exhibit(BaseExhibit):
    """ Exponat c. 107, zvukove pexeso
    mierna zmena: svetiace tlacidla nemaju zvuk (ignoruju sa)
    """

    def __init__(self, invoker,  env, settings):
        BaseExhibit.__init__(self, invoker=invoker, env=env, settings=settings)
        self.env.game_load.listen_once(self.reset_game)

    @info
    def reset_game(self):
        BaseExhibit.reset_game(self, qr_register=True)
        self.init_game()
        self.wait_first_move()

    @info
    def init_game(self):
        self.sound_theme = random.choice(self.st.sound_sets.keys())
        self.sounds = random.sample(self.st.sound_sets[self.sound_theme], 8)
        self.sounds = self.sounds + self.sounds
        random.shuffle(self.sounds)
        self.score = 0
        self.seven_print(0, '%d')
        self.is_closed = [True for x in range(16)]
        self.first_key = None # just label of key
        self.second_key = None # just label of key

    @info
    def play_sound(self, key_label):
        self.env.play_sound(self.sounds[self.st.buttons.index(key_label)]) 

    @info
    def catch_key_first(self, key, whatever):
        if key.label == self.st.start_button:
            self.reset_game()
            return
        key_number = self.st.buttons.index(key.label)
        if not self.is_closed[key_number]:
            self.wait_first_move()
            return
        self.first_key = key.label
        self.first_move()

    @info
    def wait_first_move(self):
        """Call first_move() after good key was pressed.
        Good key will be saved in self.first_key
        """
        self.env.keyboard.listen_once(self.catch_key_first, key_down)

    @info
    def first_move(self):
        """Responses for first_key press.
        """
        self.play_sound(self.first_key)
        self.make_blink()
        self.wait_second_move()

    @info
    def catch_key_second(self, key, whatever):
        if key.label == self.st.start_button:
            self.reset_game()
            return
        key_number = self.st.buttons.index(key.label)
        if not self.is_closed[key_number]:
            self.wait_second_move()
            return
        if key.label == self.first_key:
            self.wait_second_move()
            return
        self.second_key = key.label
        self.second_move()


    @info
    def wait_second_move(self):
        """Call second_move() after good key was pressed.
        Good key will be saved in self.second_key
        """
        self.qr_unregister()
        self.env.keyboard.listen_once(self.catch_key_second, key_down)


    @info
    def second_move(self):
        """Responses for second_key press.
        """
        self.play_sound(self.second_key)
        self.end_move()

    @info
    def end_move(self):
        """
        """
        self.score += 1
        self.seven_print(self.score, '%d')
        self.make_unblink() 
        if self.sounds[self.st.buttons.index(self.first_key)] == self.sounds[self.st.buttons.index(self.second_key)]:
            self.env.light(self.first_key, 1)
            self.env.light(self.second_key, 1)
            self.is_closed[self.st.buttons.index(self.first_key)] = False
            self.is_closed[self.st.buttons.index(self.second_key)] = False

        game_over = True
        for x in self.is_closed:
            if x == True: # undiscovered are still present
                game_over = False
        
        if game_over:
            self.end_game()
        else:
            self.wait_first_move()

    @info
    def blink(self, whatever):
        self.env.light(self.first_key, 1 - (self.env.lights[self.first_key]) )

    @info
    def make_blink(self):
        self.blinking_timer = self.create_timer(float('inf'), self.st.blinking_interval,
                callback = self.blink)
        self.blinking_timer.start()

    @info
    def make_unblink(self):
        self.blinking_timer.cancel()
        self.env.light(self.first_key, 0)

    @info
    def end_game(self):
        BaseExhibit.end_game(self)
        #logger.info(str(self.user_id))
        #self.env.upload_game_results(exponat_name=self.st.exhibit.name, user_id=self.user_id, score=self.score,
        #        level=self.st.level.name, timeout=10)
        #self.html('html_score')
        self.seven_flicker(texts=self.score, phormats="%d", lengths=self.env.seven_length,
                callback=self.reset_game)
