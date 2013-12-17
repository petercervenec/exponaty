from pkg.emulator import Emulator
from pkg.general import Invoker, FakeQrScanner
from pkg.settings import Game91Settings
import random
import time

settings=Game91Settings('emulator')
settings.qr_factory=FakeQrScanner
invoker=Invoker()
env=Emulator(invoker, settings)

for i in range(24*3600):
        env.play_sound(random.choice(list(env.samples.keys())))
time.sleep(24*3600)
env.__exit__()
