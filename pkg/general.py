# vim: set expandtab:

from time import (
        time,
        sleep
        )

from threading import (
        Thread,
        Condition,
        )

import sys
import os

from collections import deque
import logging
import subprocess
import re
import signal
from functools import partial

def info(fn):
    def _fn(*args, **kwargs):
        logger.info(fn.__name__+' '+str(args)+' '+str(kwargs))
        return fn(*args, **kwargs)
    return _fn

def debug(fn):
    def _fn(*args, **kwargs):
        logger.debug(fn.__name__)
        return fn(*args, **kwargs)
    return _fn

with open('expo.log', 'w'):
    pass
logger = logging.getLogger('expo')
hdlr = logging.FileHandler('expo.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.INFO)
logger.info('---')

class Popen(subprocess.Popen):
    """
    our implementation of Popen: 
    1) added __enter__ and __exit__ methods (as they are in Python v. 3, such that 'with' statement works properly; 
    2) process creates its own destructor called end_function, which is put into env.finishing_list 
    3) added early_exit method, that exits process (using its end_function)
    
    warning: as we found out, even with __enter__ and __exit__ implemented as bellow, proceses are
    not closed correctly in multithreading environment: __exit__ is not called in daemon thread, if
    the main thread wants to exit. To patch this behavior, env.finishing_list was introduced.
    """

    def __init__(self, env, *args, **kwargs):
        logger.info('Popen.__init__()')
        kwargs['preexec_fn']=os.setsid
        subprocess.Popen.__init__(self, *args, **kwargs)
        self.env = env
        self.end_function = lambda: self.__exit__()
        env.finishing_list.append(self.end_function)

    def __enter__(self):
        logger.info('Popen.__enter__()')
        return self

    @info
    def early_exit(self, type=None, value=None, traceback=None):
        try:
            self.env.finishing_list.remove(self.end_function)
        except Exception as e:
            logger.error(e)
        self.__exit__()

    @info
    def __exit__(self, type=None, value=None, traceback=None):     
        try:
            if self.stdout:
                self.stdout.close()
            if self.stderr:
                self.stderr.close()
            if self.stdin:
                self.stdin.close()
        except Exception:
            pass
        try:
            os.killpg(os.getpgid(self.pid), signal.SIGKILL)
            self.wait()
        except Exception:
            pass

class EventProducer:
    """
    base class for object that can produce events. When an event is produced, it fires all
    registered callbacks; for execution it uses its own invoker instance
    """
    def __init__(self, invoker, parent=None):
        self.callbacks=[]
        self.invoker = invoker
        self.parent=parent

    def __add_callback__(self, callback, once=True, philter=None):
        """
        function `callback` will be called whenever an event is fired; function will be called with
        arguments specific to the event. Callback is called only if `philter(*args)` resolves to
        True; furhermore, if `once` is set, callback is removed after first invocation (with respect
        to `philter`)

        typical use-case for philter are general.key_down (or general.key_up) that filters only
        key_down key event

        """
        def _callback(*args, **kwargs):
            callback(*args, **kwargs)
        to_append=(_callback, once, philter)
        self.callbacks.append(to_append)
        return to_append

    def listen(self, callback, philter=None):
        return self.__add_callback__(callback, once=False, philter=philter)

    def listen_once(self, callback, philter=None):
        return self.__add_callback__(callback, once=True, philter=philter)

    def fire_event(self, *args, **kwargs):
        """
        fires event to the all listeners
        """
        logger.debug('fire event %s %s' % (str(self), str(args)))
        to_remove=[]
        for callback in self.callbacks:
            fn, once, philter=callback
            if (not philter) or philter(*args, **kwargs):
                self.invoker.invoke(fn, *args, **kwargs)
                if once:
                    to_remove.append(callback)
        self.callbacks=[callback for callback in self.callbacks if callback not in to_remove]
        if self.parent:
            self.parent.fire_event(*args, **kwargs)

    def remove_callback(self, cb):
        """
        removes specific callback
        """
        self.callbacks.remove(cb)

    def remove_callbacks(self):
        """
        removes all callbacks
        """
        self.callbacks=[]

class Key(EventProducer):
    """ Representing one Key
        Properties:
         -- keydown, keyup: EventProducer
         -- key_object: depends on env
         -- label: str
         -- pressed: bool
    """

    def __init__(self, invoker, key_object, label, keyboard):
        EventProducer.__init__(self, invoker, parent=keyboard)
        self.key_object = key_object
        self.label = label
        self.pressed = False

    def fire_event(self, updown):
        EventProducer.fire_event(self, self, updown)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return '''Key('%s')'''%self.label

class QrScanner(EventProducer):
    """

    """
    def __init__(self, invoker, settings, env, callback=None, end_callback=None):
        EventProducer.__init__(self, invoker)
        self.callback = callback
        self.end_callback = end_callback
        self.st = settings
        self.env = env

    @info
    def start(self):
        def _start():
            try:
                def _child_exit():
                    os.system('pkill barcode')
                    os.system('pkill zbarcam')
                self.env.finishing_list.append(_child_exit)
                with Popen(self.env, self.st.barcode_command, shell=False, stdout=subprocess.PIPE) as child:
                    self.process=child
                    current_code = ""
                    while True:
                        out = child.stdout.read(1)
                        if out == '' and child.poll() != None:
                            break
                        if out != '\n':
                            current_code = current_code + out
                        if out == '\n':
                            try: 
                                reg=r'USER_ID=\d+'
                                ans = re.findall(reg, current_code)
                                if len(ans) == 0:
                                    logger.warn('QR code does not match USER_ID=sth pattern: ' + current_code)
                                else:
                                    self.fire_event(ans[0])
                            except Exception as e:
                                logger.exception(e)
                            current_code = ""
            except Exception as e:
                logger.exception(e)

        t = Thread(target=_start)
        t.daemon = True
        t.start()

class FakeQrScanner(EventProducer):
    """
    fake qr-scanner for debugging. When F2-F4 keys are pressed it emulates user with id 1-3
    (respectively) to be qr-scanned (works only with emulator env)
    """
    def __init__(self, invoker, *args, **kwargs):
        self.key2user_id = {
                'f2': 1,
                'f3': 2,
                'f4': 3,
                }
        EventProducer.__init__(self, invoker)

    def fire_event(self, key):
        data = 'USER_ID='+str(self.key2user_id[key])
        EventProducer.fire_event(self, data)

    def start(*args, **kwargs):
        pass

    def __exit__(self):
        pass


class Keyboard(EventProducer):
    """Representing the whole keyboard
        Properties:
         -- keys: list of Key objects
    """

    def __init__(self, invoker, key_map):
        EventProducer.__init__(self, invoker)
        self.keys = [Key(invoker, letter, label, self) for label, letter in key_map.items()]

    def find_key(self, label):
        """Returns the key with the given label"""
        for key in self.keys:
            if key.label == label:
                return key
        return None

#convenient filter functions for __add_callback__ and listen[_once] functions.
key_down=lambda key, updown: updown=='down'
key_up=lambda key, updown: updown=='up'

def strip_params(fn):
    def _fn(*args, **kwargs):
        fn()
    return _fn

def __pass__(*args, **kwargs):
    pass

class Timer(EventProducer): #{{{

    """
    Timer implementation; richer than threading.Timer: allows to periodically fire one callback for
    some time, finally it fires second callback. Timer instance is tightly bound to invoker object
    which is used to execute callbacks.
    """
    def __init__(self, invoker, total=None, interval=None, callback=__pass__, end_callback=__pass__, user_data=None):
        """Run for `total` seconds, every `interval` call `callback`, finally
        call `end_callback`. If `interval` is not set, only `end_callback` is
        called once.

        If `total` is None, call until canceled.
        """
        EventProducer.__init__(self, invoker)
        self.interval = interval if interval is not None else float('inf')
        self.total = total if total is not None else float('inf')
        if user_data:
            self.callback = partial(callback, user_data=user_data)
        else: 
            self.callback = callback
        self.end_callback = end_callback
        self.user_data = user_data
        self.cancelled = False
        self.last_time = time()
        self.timer_invoker = Invoker()
        self.timer_invoker.name = 'timer invoker'
        self.end_cnd = Condition()

    def start(self):
        def __callback__():
            if not self.cancelled:
                self.callback(self.time_left)
                self.timer_invoker.invoke(tick)

        def tick():
            to_sleep = max(0, min(self.time_left, self.interval))
            with self.end_cnd:
                self.end_cnd.wait(to_sleep)
            act_time = time()
            self.time_left = self.total - (act_time - self.begin_time)
            if not self.cancelled:
                if self.time_left > 0:
                    self.invoker.invoke(__callback__)
                else:
                    self.invoker.invoke(self.end_callback)
                    self.timer_invoker.cancel()
        self.begin_time = time()
        self.time_left = self.total
        self.timer_invoker.start()
        self.timer_invoker.invoke(tick)
        return "timer_start_return"

    def cancel(self):
        self.cancelled = True
        self.timer_invoker.cancel()
        with self.end_cnd:
            self.end_cnd.notify_all()
        
#}}}


class Invoker:
    """
    once started, invoker works as a one-thread executor, executing functions that are passed to it
    using invoke
    """

    def __init__(self):
        self.cnd = Condition()
        self.commands = deque()
        self.end = False

    def start(self):
        t = Thread(target = self.__start__)
        t.daemon = True
        t.start()
        return t

    def __start__(self):
        try:
            while not self.end:
                with self.cnd:
                    while (not self.commands) and (not self.end):
                        self.cnd.wait()
                    if not self.end:
                        fn,args,kwargs=self.commands.pop()
                if not self.end:
                    logger.debug('invoking %s with arguments %s %s (%d commands left)'%(str(fn), str(args), str(kwargs), len(self.commands)))
                    fn(*args, **kwargs)
                    logger.debug('after invocation')
        except Exception as e:
            logger.exception(e)
            sys.exit()

    def __exit__(self):
        with self.cnd:
            self.end=True
            self.cnd.notify_all()

    def invoke(self, fn, *args, **kwargs):
        """
        invoke function fn with given arguments
        """
        with self.cnd:
            self.commands.appendleft((fn, args, kwargs))
            self.cnd.notify_all()
    
    def cancel(self):
        self.__exit__()


class Exhibit():
    """
    Represents exhibit level settings.
    name:   short exhibit name
    label:  ...
    id:     exhibit id (corresponds to id in specification)
    levels: list of items of type Level which correspond to levels of given
            exhibit
    """
    def __init__(self, name="", label="", id="", levels=[]):
        self.name = name
        self.id = id
        self.label = label
        self.levels = levels

    def __repr__(self):
        return "<Exhibit '%s'>" % (self.name)

    def get_level_by_name(self, name):
        """
        Returns exhibit's level with specified name.
        """
        return [level for level in self.levels if level.name == name][0]


class Level():
    """
    Contains level-specific settings.
    name:   level name
    label:  ...
    params: dictionary of level-specific parameters
    """
    def __init__(self, name="", label="", params={}):
        self.name = name
        self.params = params
        self.label = label

    def __repr__(self):
        return "<Level '%s'>" % self.name
