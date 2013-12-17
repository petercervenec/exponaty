from pkg.menu import start_menu
from pkg.settings_level import EXHIBITS
import sys
from start_expo import run

mode = 'rpi'
if len(sys.argv) > 1:
    mode = sys.argv[1]
exhibit, level = start_menu(EXHIBITS)
run(exhibit.id, level.name, mode)
