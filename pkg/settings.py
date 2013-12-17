# coding=utf-8

from collections import OrderedDict, namedtuple
from general import QrScanner, FakeQrScanner
from settings_level import EXHIBITS
from settings_html import SettingsHtml
import random
#from start_menu import find_exhibit


time_score_info = {
    'čas': (lambda exhibit, additional: additional['time'], "%.1f"),
    'skóre': (lambda exhibit, additional: exhibit.score, "%d"),
    }

score_info = {
    'skóre': (lambda exhibit, additional: exhibit.score, "%d"),
    }

time_info = {
    'čas': (lambda exhibit, additional: additional['time'], "%.1f s"),
    }


class Settings(SettingsHtml):
    def __init__(self):
        SettingsHtml.__init__(self)
        #how long flickering lasts
        self.flicker_time = 5
        #time of one flick
        self.flicker_interval = 0.3
        #how long after last activity reset should occur (if using std. reset)
        self.default_reset_time = 5
        #speed of time-ticks (rendering time on seven-segment)
        self.time_tick_interval = 0.3
        #relative path to sound samples
        self.snd_path = './pkg/samples'
        self.instr = ''
        self.key_map = {}
        self.light_map = {}
        self.bouncetime = 0.05
        self.max_score_format = "%.0f"
        self.qr_instr_time = 2
        #command to run barcode scanner
        self.barcode_command = './barcode/barcode.sh'
        #timeout for connecting with a server
        self.url_timeout = 1.5
        self.qr_factory = QrScanner
        # if True, rpi does not communicate with server (QR registration, score
        # upload, ... does not work)
        self.ignore_server = False
        self.record_sensitivity = 100  # int 1..100
        self.volume = 30  # int 0..100
        self.recording_device = "default"  # pre amixer, nie arecord
        self.sound_device = "default"  # pre amixer, nie arecord
        self.sound_device_channel = "Speaker"  # sometimes it's "Master"
        self.sound_card = "ALSA"
        self.sound_card_control = "Speaker"
        self.sound_card_control_mic = "Mic"
        #moze sa menit pri kazdom spustani, inicializuje sa pri spusteni BaseEnv.__init__()
        self.sound_card_index = None
        #set to True, if exhibit uses sound-executor-worker machinery to play sounds. if so, caches
        #all wavs to memory for faster access
        self.enable_soundworker = False
        #number of sound-workers
        self.sound_worker_count = 1
        # if having only 1 sound-worker, this kills old play process when new play process occurs
        self.one_sound_worker_mode = True
        self.web_screen=True
        self.score_line_1="nahral si"
        self.score_line_2="bodov!"

    def decorate_html(self, body):
        css = open('./main.css').read()
        return u"""
        <html>
        <head>
            <meta charset='utf-8'>
            <style type="text/css">
                {css}
            </style>
        </head>
        <body>
        {body}
        </body>
        </html>
        """.format(body=body, css=css)

    def update(self, dct):
        for key, value in dct.items():
            self.key = value
        return self

    def server_url(self):
        """Returns host and port of server.
        """
        return ("192.168.16.225", "80")


class Game82Settings(Settings):
    def __init__(self, env_type):
        Settings.__init__(self)
        self.seven_length = 6
        #self.script_command = 'arduino/placebo.sh'
        self.script_command = 'arduino/start.sh'
        self.exhibit = find_exhibit_by_id(82)
        self.level = self.exhibit.levels[0]
        self.game_time = 10
        self.threshold = 1
        self.instr = """Šľapaním do bicykla vyrob za daný čas čo najviac
                     energie."""
        self.info = {
            'čas: ': (lambda exhibit, additional: additional['time'], "%.1f"),
            'celková energia: [Ws]': (lambda exhibit, additional: exhibit.score, "%d"),
            'aktuálny výkon: [W]': (lambda exhibit, additional: exhibit.power, "%d"),
            }
    
        if env_type == 'emulator':
            ## Setup variables for emulator environment
            self.key_map = {}
            self.light_map = {}
        elif env_type == 'rpi':
            ## Setup variables for RPI environment
            self.key_map = {}
            self.light_map = {}
            self.seven_length = 3


class Game89Settings(Settings):
    def __init__(self, env_type):
        Settings.__init__(self)
        self.min_random_time = 2
        self.max_random_time = 6
        self.lighted_wall_time = 2
        self.seven_length = 0
        self.instr = """Hra pre 4 hráčov. Každý hráč má pred sebou jedno
                      tlačidlo. Hra sa aktivuje stlačením ľubovoľného tlačidla.
                      Priebeh hry: Pyramída sa v náhodnom čase rozsvieti.
                      Úlohou každého hráča je stlačiť tlačidlo čo najskôr po
                      rozsvietení pyramídy, najrýchlejší hráč dostáva bod. Hra
                      končí, keď jeden z hráčov získa 5 bodov."""

        PlayerIO = namedtuple('Player',
                              'button_label pyramid_label led_labels')
        self.playerIOs = [
            PlayerIO('a', 'Pa', ['a0', 'a1', 'a2', 'a3', 'a4']),
            PlayerIO('b', 'Pb', ['b0', 'b1', 'b2', 'b3', 'b4']),
            PlayerIO('c', 'Pc', ['c0', 'c1', 'c2', 'c3', 'c4']),
            PlayerIO('d', 'Pd', ['d0', 'd1', 'd2', 'd3', 'd4']),
            ]

        self.exhibit = find_exhibit_by_id(89)
        self.level = self.exhibit.levels[0]
        # Environment settings:
        if env_type == 'emulator':
            ## Setup variables for emulator environment
            self.key_map = OrderedDict((p.button_label, p.button_label)
                                       for p in self.playerIOs)
            self.light_map = OrderedDict((p.pyramid_label, p.pyramid_label)
                                         for p in self.playerIOs)
            for p in self.playerIOs:
                for z in p.led_labels:
                    self.light_map[z] = z
        elif env_type == 'rpi':
            #Setup variables for RPI environment
            pl = ['a', 'b', 'c', 'd']
            self.key_map = {pl[i]: (0x20, i) for i in range(4) }
            pll = ['a', 'b', 'c', 'd']
            self.light_map = {'P' + pll[i]: (0x24, 11-i) for i in range(4)}
            
            lights = [(0x20, i) for i in range(15,7,-1)] + \
                [(0x24, i) for i in range(8)] + \
                [(0x24, i) for i in range(15,11,-1)]
            i = 0
            for p in self.playerIOs:
                for z in p.led_labels:
                    self.light_map[z] = lights[i]
                    i += 1


class Game90Settings(Settings):
    def __init__(self, env_type):
        Settings.__init__(self)
        self.game_time = 10
        self.seven_lengths = (3, 3)
        self.seven_length = 6
        self.exhibit = find_exhibit_by_id(90)
        self.level = self.exhibit.levels[0]
        self.buttons = letter_stream[0:8]
        self.baby_key_labels = letter_stream[0:4]
        self.max_score_format = "%d"
        self.instr = """Traf za daný čas čo najviac rozsvietených kláves! Hru
        aktivuješ stlačením hociktorej klávesy, tlačidlá v bubne spúšťajú
        detský mód (hrá sa iba na tlačidlách v bubne)."""
        self.info = time_score_info
        if env_type == 'emulator':
            ## Setup variables for emulator environment
            self.light_map = OrderedDict((z, z) for z in self.buttons)
            self.key_map = OrderedDict((z, z) for z in self.buttons)
        elif env_type == 'rpi':
            ## Setup variables for RPI environment
            self.key_map = {self.buttons[i]: (0x20, i) for i in range(8)}
            self.light_map = {self.buttons[i]: (0x20, 15-i) for i in range(8)}


class Game91Settings(Settings):
    def __init__(self, env_type):
        Settings.__init__(self)
        self.get_color = lambda: 'varga'
        #self.wanna_be_loud
        self.span = 2
        self.enable_soundworker = True
        self.seven_length = 4
        self.seven_lengths = (4,)
        self.bouncetime=0.3
        self.exhibit = find_exhibit_by_id(91)
        self.level = self.exhibit.levels[0]
        self.midi_success_file = "pkg/samples/midi/success.mid"
        self.midi_failure_file = "pkg/samples/midi/fail.mid"
        self.instr = """Na čo najmenej stlačení nájdi klávesu s najvyšším
        tónom! Pre odovzdanie najvyššieho tónu treba stlačiť odovzdávacie
        tlačidlo v strede a potom najvyšší tón."""
        self.reset_button = 'reset'
        self.submit_button = 'submit'
        self.tone_buttons = letter_stream[2:18]
        if env_type == 'emulator':
            ## Setup variables for emulator environment
            self.key_map = OrderedDict([('reset', letter_stream[0]),
                                        ('submit', letter_stream[1])])
            for z in self.tone_buttons:
                self.key_map[z] = z
        elif env_type == 'rpi':
            ## Setup variables for RPI environment
            self.bouncetime = 0.1
            self.key_map = {self.tone_buttons[i]: (0x20, i) for i in range(16)}
            self.key_map[self.reset_button] = (0x24, 0)
            self.key_map[self.submit_button] = (0x24, 1)


class Game98Settings(Settings):
    def __init__(self, env_type):
        Settings.__init__(self)
        self.game_time = 10
        self.time_tick_interval = 0.1
        self.lighted_button_time = lambda: random.uniform(3, 8)
        self.lighted_buttons = 5
        self.seven_length = 6
        self.seven_lengths = (3, 3)
        self.instr = u"""“Odklikni” za daný čas čo najviac svietiacich
        tlačidiel. Tlačidlá sa rozsvecujú aj zhášajú náhodne, za
        stlačenie zhasnutého tlačidla dostávaš ale mínus body!"""
        self.info = time_score_info
        self.exhibit = find_exhibit_by_id(98)
        self.level = self.exhibit.levels[0]
        self.buttons = letter_stream[0:32]
        # Environment settings:
        if env_type == 'emulator':
            self.light_map = OrderedDict((z, z) for z in self.buttons)
            self.key_map = OrderedDict((z, z) for z in self.buttons)
            ## Setup variables for emulator environment
        elif env_type == 'rpi':
            ## Setup variables for RPI environment
            self.bouncetime = 0.02
            self.key_map = {self.buttons[i]: (0x27, i) for i in range(16)}
            self.key_map.update({self.buttons[16+i]: (0x20, i) for i in range(16)})
            self.light_map = {self.buttons[i]: (0x24, i) for i in range(16)}
            self.light_map.update({self.buttons[16+i]: (0x26, i) for i in range(16)})


class Game99Settings(Settings):
    def __init__(self, env_type):
        Settings.__init__(self)
        self.penalty = 5
        self.penalty_timeout = 0.2
        self.second_penalty_multiple = 5
        self.seven_lengths = 3
        self.seven_length = 3
        self.exhibit = find_exhibit_by_id(99)
        self.level = self.exhibit.levels[0]

        self.instr = """
        Dostaň očko zo štartovacej do cieľovej zóny za čo najkratší čas.
        Za každý dotyk očka s dráhou dostaneš trestný čas.
        """

        # Environment settings:
        """ s: start, e: end, r: error
            naming is important and cannot change in RPi mode!
        """
        self.start_bl = 's'
        self.end_bl = 'e'
        self.error_bl = 'r'
        self.error_ll = 'r'
        if env_type == 'emulator':
            ## Setup variables for emulator environment
            self.key_map = OrderedDict((z, z) for z in ['s', 'e', 'r'])
            self.light_map = {self.error_ll: self.error_ll}
        elif env_type == 'rpi':
            ## Setup variables for rpi environment
            self.key_map = {self.start_bl: (0x20, 0),
                            self.error_bl: (0x20, 1),
                            self.end_bl: (0x20, 2)}
            self.light_map = {self.error_ll: (0x20,15)}
            self.bouncetime = 0.1


class Game100Settings(Settings):
    def __init__(self, env_type):
        Settings.__init__(self)
        self.game_time = 10
        button = 'a'
        self.seven_length = 6
        self.seven_lengths = (3, 3)
        self.exhibit = find_exhibit_by_id(100)
        self.level = self.exhibit.levels[0]
        self.time_tick_interval = 0.3
        self.instr = """
        Stlač tlačidlo čo najviackrát v priebehu daného časového intervalu.
        """
        self.info=time_score_info
        if env_type == 'emulator':
            ## Setup variables for emulator environment
            self.key_map = {button: button}
        elif env_type == 'rpi':
            ## Setup variables for rpi environment
            self.key_map = {button: (0x20, 0)}
            self.light_map = {}
            self.bouncetime = 0.02


class Game101Settings(Settings):
    def __init__(self, env_type):
        Settings.__init__(self)
        self.seven_length = 6
        self.seven_lengths = (3, 3)
        self.activation_time = 1
        self.jump_time = 0.2
        self.width_button_labels = ['1', '2', '3', '4', '5', '6', '7', '8',
                                    '9', '0', 'q', 'w', 'e', 'r', 't', 'y',
                                    'u', 'i', 'o', 'p']
        self.height_button_labels = ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k',
                                     'l', 'z', 'x', 'c', 'v', 'b', 'n', 'm',
                                     'A', 'S', 'D', 'F']
        self.instr = "Návštevníkovi sa odmeria rozpätie rúk a výška výskoku."
        self.button_labels = list(self.height_button_labels)
        self.button_labels.extend(self.width_button_labels)
        self.vertical_pos = lambda key: 130 + self.height_button_labels.index(key.label) * 5.37
        def horisontal_pos(key):
            i = self.width_button_labels.index(key.label)
            if i == 0:
                return 0
            else:
                return 94 + 5.37 * (i-1)
        self.horizontal_pos = horisontal_pos
        self.exhibit = find_exhibit_by_id(101)
        self.exhibit.name_width = 'rozpatie_ruk'
        self.exhibit.name_height = 'vyska_vyskoku'
        self.level = self.exhibit.levels[0]
        self.instr = """Zmeraj si rozpätie rúk a výšku výskoku! Rozpätie rúk
        zmeriaš stlačením čo najvziadenejších tlačidiel. Pre aktiváciu merania
        výšky výskoku najprv dlho podrž stlačené najvyššie tlačidlo, na ktoré
        dočiahneš zo zeme. Potom vyskoč a stlač čo najvyššie tlačidlo."""

        # Environment settings:
        if env_type == 'emulator':
            ## Setup variables for emulator environment
            self.light_map = OrderedDict((z, z) for z in self.height_button_labels)
            self.key_map = OrderedDict((z, z) for z in self.button_labels)
        elif env_type == 'rpi':
            ## Setup variables for RPI environment
            keys_height = [(0x20, i) for i in range(8)] + \
                          [(0x20, i) for i in range(15,7,-1)] + \
                          [(0x22, i) for i in range(4)]
            keys_width = [(0x22, i) for i in range(4,8)] + \
                         [(0x22, i) for i in range(15,7,-1)] + \
                         [(0x21, i) for i in range(8)]
            lights = [(0x21, i) for i in range(15,7,-1)] + \
                     [(0x24, i) for i in range(8)] + \
                     [(0x24, i) for i in range(15,11,-1)]
            nhbl = len(keys_height)
            for hbl in self.height_button_labels:
                self.key_map[hbl] = keys_height[nhbl - 1 - self.height_button_labels.index(hbl)]
                self.light_map[hbl] = lights[nhbl - 1 -self.height_button_labels.index(hbl)]
            for wbl in self.width_button_labels:
                self.key_map[wbl] = keys_width[self.width_button_labels.index(wbl)]

    def html_score(self, exhibit):
        width = self.max_score_format % (exhibit.width,) if exhibit.width is not None else ''
        height = self.max_score_format % (exhibit.jump_height,) if exhibit.jump_height > 0 else ''
        return u"""
        {header}
        <div class='score'>
            <div class="score_key"> tvoje rozpätie rúk je </div>
            <div class="score_value"> {width} cm </div> </br>
            <div class="score_key"> tvoja výška výskoku je </div>
            <div class="score_value"> {height} cm </div>
        </div>
        {footer}
        """.format(header=self.html_header(exhibit),
                   footer=self.html_footer(exhibit),
                   width=width,
                   height=height,)


class Game102Settings(Settings):
    def __init__(self, env_type):
        Settings.__init__(self)
        self.time_tick_interval = 0.01
        self.seven_lengths = (3,)
        self.seven_length = 3
        self.instr = """Hru aktivuješ stlačením tlačidla. Po aktivácii hry
        prebehne náhodný čas, po uplynutí ktorého sa začne na displeji
        odpočítavať čas. Tvojou úlohou je stlačiť tlačidlo čo najrýchlejšie po
        začiatku odpočítavania."""
        self.random_time = lambda: random.uniform(2, 8)
        self.exhibit = find_exhibit_by_id(102)
        self.level = self.exhibit.levels[0]
        self.max_score_format = "%.3f"
        self.info=time_info
        self.score_line_1 = "Stihol si to za"
        self.score_line_2 = "sekúnd"
        
        # Environment settings:
        if env_type == 'emulator':
            ## Setup variables for emulator environment
            self.button = 'a'
            self.key_map = OrderedDict([('a', 'a')])
        elif env_type == 'rpi':
            ## Setup variables for RPI environment
            self.key_map = {'a': (0x26, 0)}
            self.light_map = {}
            self.bouncetime = 0.1


class Game104Settings(Settings):
    def __init__(self, env_type):
        Settings.__init__(self)
        self.qr_factory = FakeQrScanner
        self.command = "play -t alsa -n synth sin %d gain -30"
        self.seven_length = 7
        self.sound_card = "Device"
        self.tones = [10,  12,  14,  17,  21,  25,  30,  37,  44,  53, 64,  77,
                      92,  110,  133,  159,  191,  230,  276,  331, 397, 476,
                      572,  686,  824,  989,  1186,  1424,  1709,  2050,  2461,
                      2953,  3544,  4252,  5103,  6124,  7348,  8818,  10582,
                      12698, 13452, 14234, 15238, 16234, 17826, 18286, 19814, 20246, 21943, ]
        self.minus_button = 'q'
        self.plus_button = 'w'
        self.exhibit = find_exhibit_by_id(104)
        self.level = self.exhibit.levels[0]
        self.instr = """Nájdi hraničné frekvencie zvuku, ktoré ešte počuješ."""
        if env_type == 'emulator':
            ## Setup variables for emulator environment
            self.light_labels = []
            self.key_map = {k: k for k in [self.minus_button, self.plus_button]}
        elif env_type == 'rpi':
            ## Setup variables for RPI environment
            self.key_map = {self.minus_button: (0x20, 0),
                            self.plus_button: (0x20, 1)}
            self.light_map = {}
            self.bouncetime = 0.05


class Game105Settings(Settings):
    def __init__(self, env_type):
        Settings.__init__(self)
        self.seven_length = 5
        self.script_command = 'audio_recording/vol_pipe.sh'
        self.pipe_source = 'tmp/pipe'
        #self.buffer_size = 5 # achtung! there must extra byte for '/n'
        self.threshold = 7 
        self.record_sensitivity = 1  # int 1..100
        self.exhibit = find_exhibit_by_id(105)
        self.level = self.exhibit.levels[0]
        self.instr = """Čo najhlasnejšie zakrič do lievika."""
        self.info = score_info
        self.buffer_size = 50000
        self.sound_card = "Device"
        if env_type == 'emulator':
            ## Setup variables for emulator environment
            self.key_map = {}
            self.light_map = {}
        elif env_type == 'rpi':
            # TODO: Setup variables for RPI environment
            self.key_map = {}
            self.light_map = {}


class Game107Settings(Settings):
    def __init__(self, env_type):
        Settings.__init__(self)
        self.seven_length = 4
        self.seven_lengths = (4,)
        self.buttons = letter_stream[0:16]
        self.start_button = 'z'
        self.blinking_interval = 0.3
        self.exhibit = find_exhibit_by_id(107)
        self.level = self.exhibit.levels[0]
        self.enable_soundworker = True
        self.sound_card = "ALSA"

        self.sound_sets = {
            'sada_01': [
                "global_cut/apert2.wav",
                "global_cut/apert.wav",
                "global_cut/applause.wav",
                "global_cut/beam2.wav",
                "global_cut/beam.wav",
                "global_cut/cow.wav",
                "global_cut/curve.wav",
                "global_cut/drama.wav",
                "global_cut/explos.wav",
                "global_cut/fail.wav",
                "global_cut/falling.wav",
                "global_cut/glasses.wav",
                "global_cut/gong.wav",
                "global_cut/horse.wav",
                "global_cut/kling.wav",
                "global_cut/kongas.wav",
                "global_cut/laser.wav",
                "global_cut/left.wav",
                ],
            'sada_02': [
                "global_cut/nature1.wav",
                "global_cut/nature2.wav",
                "global_cut/ok.wav",
                "global_cut/pluck.wav",
                "global_cut/roll.wav",
                "global_cut/romans.wav",
                "global_cut/soft.wav",
                "global_cut/space2.wav",
                "global_cut/space3.wav",
                "global_cut/space.wav",
                "global_cut/sparcle.wav",
                "global_cut/strom.wav",
                "global_cut/theetone.wav",
                "global_cut/top.wav",
                "global_cut/train.wav",
                "global_cut/untie.wav",
                "global_cut/ups.wav",
                "global_cut/wallewal.wav",
                ],
        }

        self.instr = """Zvukové pexeso. Nájdi dvojice rovnakých zvukov! Hru
        spustíš stlačením tlačítka ŠTART."""
        if env_type == 'emulator':
            self.light_map = OrderedDict((z, z) for z in letter_stream[0:16])
            self.key_map = OrderedDict((b, b) for b in self.buttons + [self.start_button])
        elif env_type == 'rpi':
            ## Setup variables for RPI environment
            self.bouncetime = 0.1
            self.key_map = {self.buttons[i]: (0x20, i) for i in range(16)}
            self.key_map[self.start_button] = (0x24, 0)
            self.light_map = {self.buttons[i]: (0x22, i) for i in range(16)}


class GameTestSettings(Settings):
    def __init__(self, env_type):
        Settings.__init__(self)
        self.exhibit = find_exhibit_by_id('Test')
        self.seven_length = 4
        self.level = self.exhibit.levels[0]
        self.instr = """Test."""
        if env_type == 'emulator':
            keys = ['a', 's', 'd', 'f']
            lights = ['a', 's', 'd']
            self.key_map = OrderedDict((z, z) for z in keys)
            self.light_map = OrderedDict((z, z) for z in lights)
        elif env_type == 'rpi':
            self.key_map = OrderedDict()
            self.light_map = OrderedDict()
            for i, z in enumerate('abcdefgh'):
                self.light_map[z] = (0x26, i)
                self.key_map[z] = (0x26, i+8)
                print(z, i+8)
            self.bouncetime = 0.05

letter_stream = ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p',
                 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l',
                 'z', 'x', 'c', 'v', 'b', 'n', 'm',
                 '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']


def find_exhibit_by_name(name):
    for exhibit in EXHIBITS:
        if exhibit.name == name:
            return exhibit


def find_exhibit_by_id(id):
    for exhibit in EXHIBITS:
        if exhibit.id == id:
            return exhibit
