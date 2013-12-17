# vim: set expandtab:

import random
import os
import threading

from pkg.general import (
        key_down,
        key_up,
        strip_params,
        info,
        logger
        )

from pkg.base_exhibit import BaseExhibit

class Exhibit(BaseExhibit):
    """ Exponat c. 91 - klavir
    """

    @info
    def __init__(self, invoker, env, settings):
        BaseExhibit.__init__(self, invoker, env, settings)
        self.env.game_load.listen_once(self.reset_game)
        self.env.game_load.listen_once(self.qr_register)

    @info
    def reset_game(self, data=None):
        BaseExhibit.reset_game(self)
        self.init_game()
        #self.env.keyboard.listen_once(strip_params(self.begin_game))
        self.begin_game()

    def set_score(self, score):
        self.score=score
        self.seven_print_str(str(score))

    @info
    def init_game(self):
        tones=[20+i*self.st.span for i in range(16)]
        self.max_tone = max(tones)
        self.min_tone = min(tones)
        tones=[("tones/{color}/{num}".format(color=self.st.get_color(), num=num), num) for num in tones]
        #random.shuffle(tones)
        tone_keys=[key for key in self.env.keyboard.keys if key.label not in ['reset', 'submit']]
        if len(tones)!=len(tone_keys):
            raise Exception
        self.tone_map={key:tone for key,tone in zip(tone_keys, tones)}
        self.submit=False
        self.set_score(0)

    @info
    def begin_game(self):
        #BaseExhibit.begin_game(self) vypnute kvoli qr_unregister()
        self.env.keyboard.listen(self.button_down, key_down)

    @info
    def button_down(self, key, updown):
        if key.label == 'reset':
            self.reset_game()
        elif key.label == 'submit':
            self.submit=True
        else:
            self.set_score(self.score+1)
            sound,num=self.tone_map[key]
            self.env.play_sound(sound)
            if self.submit:
                self.submit=False
                if num==self.max_tone:
                    self.env.play_sound('global/applause')
                    self.end_game()
                else:
                    self.env.play_sound('global/fail')
                    self.set_score(self.score+3)

    @info
    def end_game(self):
        BaseExhibit.__reset__(self)
        #BaseExhibit.end_game(self)
        logger.info(str(self.user_id))
        self.env.upload_game_results(exponat_name=self.st.exhibit.name, user_id=self.user_id, score=self.score,
                level=self.st.level.name, timeout=10)
        self.html('html_score')
        ## end of BaseExhibit.end_game(self)
        self.seven_flicker(self.score, "%d", callback=self.reset_game)

