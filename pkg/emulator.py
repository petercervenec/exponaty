# vim: set expandtab:

from pkg.general import (
        EventProducer,
        logger,
        strip_params,
        Key,
        Keyboard,
        )
from pkg.base_env import BaseEnv
from collections import OrderedDict
from threading import Thread, Timer
from functools import partial
import threading
import os
import urwid
import gtk
import gobject as gob
import sys
import time

class Emulator(BaseEnv):
    """Emulator that uses computer keyboard as a keyboard for the game and computer display for all
    kind of displays

    """

    def __init__(self, invoker, settings):
        """
        see BaseEnv.__init__
        for convenience reasons, light_map can be either dict or list; in latter case it is changed
        to trivial {z:z} dict
        """
        BaseEnv.__init__(self, invoker, settings)
        #initialize urwid widgets 
        self.info_textbox = urwid.Text("")
        self.light_textbox = urwid.Text('')
        self.seven_textbox = urwid.Text('')
        self.keys_textbox = urwid.Text('')
        self.qr_textbox = urwid.Text('')
        div = urwid.Divider()
        pile = urwid.Pile([self.info_textbox, div, self.light_textbox, div, self.seven_textbox,
            self.keys_textbox, self.qr_textbox])
        top = urwid.Filler(pile, valign='middle')
        self.loop=urwid.MainLoop(top, unhandled_input=self.__handle_keypress__)

    def run(self, info=""):
        """At the moment of the load of the environment, game_load event gets
        fired. Exponate can listen to this event and do some initializations.
        """
        #tick schedules recursive sequence of ticks with fixed time-period -
        #needed for urwid responsiveness
        def tick():
            self.loop.set_alarm_in(0.1, strip_params(tick))
        tick()
        #start game when main_loop is created
        self.urwid_invoke(self.game_load.fire_event)
        self.urwid_invoke(self.refresh_keys)
        if self.st.web_screen:
            self.start_gtk_thread()
        # Loop is specific attribute for Emulator environment; because of
        # urwid, loop.run() must be called in the main thread after all
        #initialization.
        self.loop.run()
        logger.info('urwid main-loop exited')

    def urwid_invoke(self, cb):
        """
        invoke cb in the urwid's mainloop thread
        """
        self.loop.set_alarm_in(0,strip_params(cb))

    def _seven_print(self, text):
        """Prints the text using the 7-segment display"""
        self.seven_text=text
        def _cb(self):
            self.seven_textbox.set_text("7digit: %s" % text)
        self.urwid_invoke(partial(_cb, self))

    def light(self, label, state):
        """
        Changes the state of the light corresponding to the `label` to the value
        described by `state`. Possible values for `state` are 0 for light off and 1
        for light on.
        """
        self.lights[label]=state
        def cb():
            self.light_textbox.set_text("Lights: %s" % self._lights_to_str())
            self.loop.draw_screen()
        self.urwid_invoke(cb)

    def refresh_keys(self):
        """
        redraw keys according to their actual states
        """
        def cb():
            self.keys_textbox.set_text("Keys: %s" % self._keys_to_str())
            self.loop.draw_screen()
        self.urwid_invoke(cb)

    def _lights_to_str(self):
        """
        pretty print lights
        """
        return("   ".join("%s: %s"%(label, '*' if value else ' ') for label,value in self.lights.items()))


    def _keys_to_str(self):
        """pretty print keys"""
        return "   ".join("%s: %s" % (key.label, '*' if key.pressed else ' ') for key in self.keyboard.keys)


    def __handle_keypress__(self, letter):
        if letter=='esc':
            logger.info('exiting program (escape pressed)')
            BaseEnv.__exit__(self)
            if self.st.web_screen:
                self.main_window.destroy()
                gob.idle_add(gtk.main_quit)
            raise urwid.ExitMainLoop()
            self.invoker.__exit__()
            sys.exit()
            
        elif hasattr(self.qr,'key2user_id') and letter in self.qr.key2user_id.keys():
            self.qr.fire_event(letter)

        else:
            for key in self.keyboard.keys:
                if key.key_object==letter:
                    key.pressed=not key.pressed
                    updown='down' if key.pressed else 'up'
                    key.fire_event(updown)
            self.refresh_keys()


