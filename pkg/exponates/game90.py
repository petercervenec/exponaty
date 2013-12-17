import random

from pkg.general import (
        logger,
        key_down,
        strip_params,
        info,
        )

from pkg.base_exhibit import BaseExhibit

class Exhibit(BaseExhibit):
    """
    meassuring of reaction, lights bulbs randomly, player has to press corresponding button as fast
    as possible
    """
    def __init__(self, invoker,  env, settings):
        BaseExhibit.__init__(self, invoker=invoker, env=env, settings=settings)
        self.env.game_load.listen_once(self.reset_game)

    @info
    def reset_game(self, qr_register=True):
        BaseExhibit.reset_game(self, qr_register=qr_register)
        self.init_game()
        self.env.keyboard.listen_once(self.begin_game)

    @info
    def init_game(self):
        self.score = 0
        self.last_key = None
        self.is_baby = False

    @info
    def answered(self, key, updown):
        self.score += 1
        self.env.light(key.label, 0)
        self.move()

    @info
    def move(self):
        while True:
            key=random.choice(self.env.keyboard.keys)
            if key!=self.last_key:
                if self.is_baby and key.label in self.st.baby_key_labels:
                    break
                if not self.is_baby:
                    break
        self.last_key=key
        self.env.light(key.label, 1)
        key.listen_once(self.answered, key_down)

    @info
    def begin_game(self, key, updown):
        """Starts new game; if first key is baby key, it starts game in the baby
        mode using only lower 4 keys.
        """
        BaseExhibit.begin_game(self)
        if key.label in self.st.baby_key_labels:
            self.is_baby=True
        self.create_timer(self.st.game_time, self.st.time_tick_interval,
            callback=self.update_display,
            end_callback=self.end_game
            ).start()
        self.run_reset_timer(self.reset_game)
        self.move()

    def update_display(self,t):
        BaseExhibit.update_display(self,t)
        self.seven_print(texts=(t,self.score), phormats=("%.1f", "%d"))

    @info
    def end_game(self):
        BaseExhibit.__reset__(self)
        BaseExhibit.end_game(self)
        self.seven_flicker(texts=self.score, phormats="%d", lengths=self.env.seven_length,
                callback=self.reset_game)
