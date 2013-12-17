import time
from pkg.general import (
    logger,
    key_down,
    key_up,
    strip_params,
    info,
    )
from pkg.base_exhibit import BaseExhibit


class Exhibit(BaseExhibit):
    def __init__(self, invoker, env, settings):
        BaseExhibit.__init__(self, invoker=invoker, env=env, settings=settings)
        self.env.game_load.listen_once(self.reset_game)
        self.height_key_down = lambda key, updown: key.label in self.st.height_button_labels and updown == 'down'
        self.height_key_up = lambda key, updown: key.label in self.st.height_button_labels and updown == 'up'
        self.width_key_down = lambda key, updown: key.label in self.st.width_button_labels and updown == 'down'

    def reset_game(self):
        BaseExhibit.reset_game(self, qr_register=True)
        self.width = None
        self.max_width = 0
        self.jump_height = None
        self.max_height = 0  # max_jump_height = self.max_height - self.vertical_base
        self.max_jump_height = None
        self.last_jump = 0
        self.vertical_base = None
        self.base_timers = {}
        self.update_display()
        self.env.keyboard.listen(self.measure_width, self.width_key_down)
        self.env.keyboard.listen(self.process_height_button_press, self.height_key_down)
        self.env.keyboard.listen(self.remove_base_callback, self.height_key_up)
        self.env.keyboard.listen(self.measure_jump_height, self.jump_key_up)

    def measure_width(self, key, updown):
        pressed = [self.env.keyboard.find_key(label) for label in
                   self.st.width_button_labels if self.env.keyboard.find_key(label).pressed]
        if len(pressed) >= 2:
            positions = [self.st.horizontal_pos(k) for k in pressed]
            self.width = max(positions) - min(positions)
            self.max_width = max(self.width, self.max_width)
            self.update()

    @info
    def process_height_button_press(self, key, updown):
        key.last_pressed = time.time()
        self.base_timers[key] = self.create_timer(
            self.st.activation_time,
            end_callback=lambda: self.set_base(key),
            user_data=key)
        self.base_timers[key].start()

    @info
    def remove_base_callback(self, key, updown):
        if key in self.base_timers.keys() and not self.base_timers[key].cancelled:
            self.base_timers[key].cancel()

    @info
    def measure_jump_height(self, key, updown):
        height = self.st.vertical_pos(key)
        jump_height = height - self.vertical_base
        now = time.time()
        if now - self.last_jump > self.st.jump_time:
            self.jump_height = jump_height
            self.last_jump = now
            self.create_timer(self.st.jump_time, end_callback=self.update).start()
        else:
            self.jump_height = max(jump_height, self.jump_height)
        self.max_height = max(self.max_height, height)
        self.max_jump_height = self.max_height - self.vertical_base

    @info
    def update(self):
        self.update_display()
        self.env.upload_game_results(exponat_name=self.st.exhibit.name_height,
                                     user_id=self.user_id,
                                     score=self.jump_height,
                                     level=self.st.level.name,
                                     timeout=self.st.url_timeout)
        self.env.upload_game_results(exponat_name=self.st.exhibit.name_width,
                                     user_id=self.user_id,
                                     score=self.width,
                                     level=self.st.level.name,
                                     timeout=self.st.url_timeout)
        self.update_max_score()
        self.update_display()

    @info
    def set_base(self, base_key):
        self.vertical_base = self.st.vertical_pos(base_key)
        for label in self.st.light_map.keys():
            if self.st.vertical_pos(self.env.keyboard.find_key(label)) > self.vertical_base:
                self.env.light(label, 1)
            else:
                self.env.light(label, 0)
        self.base_timers[base_key].cancel()

    def jump_key_up(self, key, updown):
        return self.vertical_base is not None and \
            key.label in self.st.height_button_labels and \
            self.st.vertical_pos(key) > self.vertical_base and \
            hasattr(key, 'last_pressed') and time.time() - key.last_pressed < self.st.activation_time and \
            updown == 'up'

    @info
    def update_display(self):
        width = str(self.width) if self.width else "---"
        height = str(self.jump_height) if self.jump_height > 0 else "---"
        self.seven_print(texts=(width, height), phormats=('%3s', '%3s'))
        self.html('html_score')

    def update_max_score(self):
        width = self.env.get_max_score(self.st.exhibit.name_width, self.st.level.name, timeout=self.st.url_timeout)
        height = self.env.get_max_score(self.st.exhibit.name_height, self.st.level.name, timeout=self.st.url_timeout)
        if isinstance(width, float):
            self.max_score_width = self.st.max_score_format % (width,)
        if isinstance(height, float):
            self.max_score_height = self.st.max_score_format % (height,)

    def get_max_score(self):
        res = ''
        if hasattr(self, 'max_score_width'):
            res += self.max_score_width + '/'
        if hasattr(self, 'max_score_height'):
            res += self.max_score_height
        return res
