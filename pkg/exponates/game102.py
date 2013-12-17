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
        self.infinite_timer=None

    @info
    def reset_game(self,qr_register=True):
        BaseExhibit.reset_game(self,qr_register=qr_register)
        self.infinite_timer = None
        self.magic_timer = False
        self.env.keyboard.listen_once(strip_params(self.begin_game), key_down)

    @info
    def begin_game(self):
        BaseExhibit.begin_game(self)
        self.seven_print(texts='', phormats="%s")
        self.wait_timer=self.create_timer(self.st.random_time(),
                end_callback=self.start_infinite_timer)
        self.wait_timer.start()
        self.env.keyboard.listen_once(strip_params(self.handle_button_press), key_down)

    @info
    def start_infinite_timer(self):
        self.beginning = time.time()
        self.run_reset_timer(lambda: self.reset_game(qr_register=True))
        self.infinite_timer=self.create_timer(60, self.st.time_tick_interval, callback = strip_params(self.tick))
        self.infinite_timer.start()
    
    def tick(self):
        act_time=time.time()
        self.score=act_time-self.beginning
        self.seven_print(texts=self.score, phormats="%.2f")
        self.update_display(self.score)

    @info
    def handle_button_press(self):
        if self.infinite_timer:
            self.stop_reset_timer()
            self.infinite_timer.cancel()
            self.seven_flicker(texts=self.score, phormats="%.2f", callback=strip_params(self.reset_game))
            self.infinite_timer=None
            BaseExhibit.end_game(self)
        else:
            self.wait_timer.cancel()
            logger.info(str(self.user_id))
            self.seven_flicker(texts='err', phormats="%s", callback=strip_params(self.reset_game))
            self.env.upload_game_results(exponat_name=self.st.exhibit.name, user_id=self.user_id, score=None,
                level=self.st.level.name, additional_data={'cheater':True})

