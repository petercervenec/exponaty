# vim: set expandtab:

from pkg.emulator import Emulator
from pkg.general import Invoker, logger
import sys


def run(expo_num, level_name, mode):
    game_str = 'game%s' % expo_num
    game_settings_str = "Game%sSettings" % expo_num
    _temp = __import__('pkg.exponates', globals(), locals(), [game_str])
    Exhibit = getattr(_temp, game_str).Exhibit
    _temp = __import__('pkg.settings', globals(), locals(),
                       [game_settings_str])
    Settings = getattr(_temp, game_settings_str)

    invoker = Invoker()
    settings = Settings(mode)

    level = None
    for l in settings.exhibit.levels:
        if l.name == level_name:
            level = l
    if level is None:
        level = settings.exhibit.levels[0]

    #inject level-specific settings into settings object
    for key, val in level.params.items():
        setattr(settings, key, val)

    #set test exhibit to selected level
    if expo_num == 'Test' and level_name != 'default':
        io_settings_str = "Game%sSettings" % level_name
        _temp = __import__('pkg.settings', globals(), locals(),
                           [io_settings_str])
        IOSettings = getattr(_temp, io_settings_str)
        io_settings = IOSettings(mode)
        settings.key_map = io_settings.key_map
        settings.light_map = io_settings.light_map
        settings.seven_length = io_settings.seven_length

    logger.info('start_expo.py, before localizing settings')
    try:
        from pkg.local_settings import localize_settings
    except Exception as e:
        logger.warn('no local settings')

    if "localize_settings" in locals():
        try:
            localize_settings(settings)
            logger.info('localizing settings')
        except Exception as e:
            logger.error("failed to load local setings")
            logger.error(e)

    if mode == 'emulator':
        env = Emulator(invoker, settings)
    else:
        from pkg.rpi_env import RpiEnv
        env = RpiEnv(invoker, settings)

    exhibit = Exhibit(invoker, env, settings)
    invoker.start()
    env.run()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('''
        usage: python[2] start_expo.py expo_number [emulator|rpi]
        ''')
        sys.exit()
    else:
        expo_num = sys.argv[1]
        mode = 'emulator'
        level_name = 'default'
    if len(sys.argv) >= 3:
        mode = sys.argv[2]
    if len(sys.argv) >= 4:
        level_name = sys.argv[3]
    run(expo_num, level_name, mode)

    # if profiling is desired, use these three lines instead of run(...) above
    #import cProfile
    #filename = '/home/marcelka/projects/expo/profile/profile-expo-'+expo_num
    #cProfile.run('run(expo_num, level_name, mode)', filename, sort=2)
