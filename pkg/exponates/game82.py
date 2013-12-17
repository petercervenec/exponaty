# vim: set expandtab:

from pkg.base_exhibit import BaseExhibit

from pkg.general import (
    logger,
    key_down,
    strip_params,
    info,
    Invoker,
    )

from time import (
    time,
    sleep
    )

from threading import Thread
from pkg.general import EventProducer
import sys
import os
import re
import subprocess
from pkg.general import Popen

global_idle = True

class EnergyInput(EventProducer):
    def __init__(self, invoker, settings, env, callback=None, end_callback=None):
        EventProducer.__init__(self, invoker)
        self.callback = callback
        self.end_callback = end_callback
        self.st = settings
        self.env = env

    def start(self):
        def _start():
            try:
                with Popen(self.env, self.st.script_command, shell=False,
                           stdout=subprocess.PIPE) as child:
                    then = 0
                    while True:
                        out = child.stdout.readline()
                        m = re.search(r'^(\d+)\t([\d.]+)\t([\d.]+)', out)
                        if m:
                            now = int(m.group(1))
                            power = float(m.group(2))*float(m.group(3))
                            energy = power * (now - then) / 1000
                            then = now
                            if global_idle == True and power <= self.st.threshold:
                                pass
                            else:
                                self.fire_event(energy, power)
                        else:
                            logger.warn('problem parsing ' + str(out))
            except Exception as e:
                logger.error(e)
        t = Thread(target=_start)
        t.daemon = True
        t.start()


class Exhibit(BaseExhibit):
    """ Exponat c. 82.
    """
    def __init__(self, invoker,  env, settings):
        global global_idle
        global_idle = True
        BaseExhibit.__init__(self, invoker=invoker, env=env, settings=settings)
        self.energy_input = EnergyInput(invoker, settings=self.st, env=self.env)

        self.env.game_load.listen_once(self.mega_reset_game)

    @info
    def mega_reset_game(self):
        self.qr_register()        
        self.energy_input.start()
        self.reset_game()

    @info
    def reset_game(self):
        BaseExhibit.reset_game(self, qr_register=True)
        self.init_game()
        self.energy_input.remove_callbacks()
        self.energy_input.listen(self.energy_listener)

    @info
    def init_game(self):
        self.time=self.st.game_time
        self.score = 0
        global global_idle
        global_idle = True

    @info
    def energy_listener(self, energy, power):
        self.power=power
        if global_idle and energy > self.st.threshold:
            self.begin_game()
            self.score = energy
        elif (not global_idle):
            self.score += energy

    @info
    def begin_game(self):
        global global_idle
        global_idle = False
        BaseExhibit.begin_game(self)
        self.create_timer(self.st.game_time, self.st.time_tick_interval, 
            callback=self.time_tick, end_callback=self.end_game).start()
    
    @info 
    def end_game(self):
        self.energy_input.remove_callbacks()
        self.html('html_score')
        BaseExhibit.end_game(self)
        self.create_timer(self.st.flicker_time, self.st.flicker_time,
                end_callback=self.reset_game).start()

    def time_tick(self, time):
        self.time = time
        self.update_display(time)
