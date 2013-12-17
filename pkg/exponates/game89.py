import random
from functools import partial

from pkg.general import (
        logger,
        key_down,
        strip_params,
        info,
        )
from pkg.base_exhibit import BaseExhibit

class Player:
    def __init__(self, io, score=0):
        self.io = io
        self.score = score

class Exhibit(BaseExhibit):
    """ four players around a table (button in front of each), pyramid in the middle of the table
        pyramid lights up at random time; player that presses his/her button first, gets a point
        5-tuple of led-diodes shows points for each player; when someone reaches 5 points, the game ends (pyramid flickers)
    """

    @info
    def __init__(self, invoker, env, settings):
        BaseExhibit.__init__(self, invoker=invoker, env=env, settings=settings)
        self.players = [Player(pio) for pio in self.st.playerIOs]
        self.env.game_load.listen_once(self.reset_game)

    @info
    def reset_game(self):
        BaseExhibit.reset_game(self)
        for p in self.players:
            p.score = 0
        self.reset_lights()
        self.env.keyboard.listen_once(strip_params(self.prepare_round), key_down)

    @info
    def prepare_round(self):
        timeout = random.uniform(self.st.min_random_time, self.st.max_random_time)
        self.create_timer(timeout, timeout, end_callback = self.begin_round).start()

    @info
    def begin_round(self):
        for p in self.players:
            logger.info('tu'+str(p.io.pyramid_label))
            self.env.light(p.io.pyramid_label, 1)
        self.env.keyboard.listen_once(self.update_scores, key_down)
        self.run_reset_timer(self.reset_game)

    @info
    def end_round(self):
        for p in self.players:
            self.env.light(p.io.pyramid_label, 0)
        self.prepare_round()

    @info
    def update_scores(self, key, updown):
        self.stop_reset_timer()
        for p in self.players:
            if p.io.button_label == key.label:
                p.score += 1
                self.env.light(p.io.led_labels[p.score-1], 1)
                if p.score == len(p.io.led_labels):
                    def blink_winner(self, p):
                        for ll in p.io.led_labels:
                            self.env.light(ll, not self.env.lights[ll])
                    self.create_timer(self.st.flicker_time,
                        self.st.flicker_interval,
                        callback = strip_params(partial(blink_winner, self, p)),
                        end_callback = self.reset_game).start()
                else:
                    self.create_timer(self.st.lighted_wall_time,
                        self.st.lighted_wall_time,
                        end_callback=self.end_round).start()
            else:
                self.env.light(p.io.pyramid_label, 0)
