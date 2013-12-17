.. _configuration:
Konfigurácia
************

Pre konfiguráciu jednotlivých exponátov sa používajú súbory: 

================== ======
súbor              význam
================== ======
settings_html.py   konfigurácia vzhľadu HTML obrazoviek
settings_level.py  konfigurácia levelov, ktoré existujú pre dané exponáty
settings.py        zvyšná konfigurácia 
================== ======

Nižšie sa nachádza sumár nastavení, ktoré bežný používateľ môže meniť. Okrem týchto, existujú
ešte aj vnútorné settings, ktoré sa meniť neodporúča, pokiaľ si daný človek nie je dostatočne vedomý
princípov fungovania produktu.

.. attention::
    Pri zásahoch do nastavení je potrebné úzko dbať na štruktúru nastavovacích súborov.

settings_html
=============
V tomto súbore sa definujú viaceré html obrazovky, spoločné pre viaceré exponáty.

================== ======
obrazovka          význam
================== ======
html_header        Header
html_footer        Footer
html_welcome       Zobrazí sa po prihlásení hráča QR-kódom
html_bye           Zobrazí sa po odhlásení hráča QR-kódom
html_info          V závislosti od ďalšej konfigurácie zobrazí užívateľovi niekoľko key-value párov hodnôt
html_instr         Inštrukcie pre hru
html_score         Zobrazí skóre po skončení hry
================== ======                                                

Ďalšie vlastnosti zobrazovania je možné upraviť v priloženom .css súbore. Presný tvar zobrazovaných
hlášok sa kvôli väčšej flexibilite čerpá zo súboru ``settings.py`` a tu sa nenachádza.


settings_level
==============
Tento súbor konfiguruje spúšťacie menu a to hlavne správanie sa jednotlivých levelov exponátov.


settings
==============
Tu sa nachádza konfigurácia samotných exponátov. Aby sa zabránilo duplicitnému písaniu nastavení,
využíva sa dedičnosť nastavení: v sekcii Settings sú definované defaultné nastavenia, jednotlivé
exponáty ich potom môžu alebo nemusia upraviť pre svoje potreby v sekciách GameXXXSettings, kde XXX
sa nahradí číslom exponátu. Settings spoločné pre viacero exponátov sú tieto:


=========================================  ======
názov premennej                            význam
=========================================  ======
seven_length                               dĺžka 7segmentového displeja
seven_lengths                              špecifikuje, na aké podčasti je displej rozdelený (napr. 6 segmentov môže byť rozdelených na 3+3, na jednej trojici sa zobrazuje skôre, na druhej čas
key_map                                    definuje mapovanie tlačidiel na expanderové adresy
light_map                                  definuje mapovanie žiaroviek na expanderové adresy
game_time                                  dĺžka trvania hry
flicker_time                               čas, ktorý bliká skóre po skončení hry
flicker_interval                           rýchlosť tohto blikania (čas medzi blikmi)
default_reset_time                         po tomto čase sa exponát zresetuje kvôli neaktivite
time_tick_interval                         interval prekresľovania hodnôt na displeji
bouncetime                                 debounce time na software úrovni
url_timeout                                timeout pre spojenie sa so serverom
qr_factory                                 factory na výrobu QrScanner, možné hodnoty sú QrScanner (štandard) alebo FakeQrScanner (vypne QR funkcionalitu)
ignore_server                              ak je True, nekomunikuje sa so serverom
record_sensitivity                         citlivosť nahrávania  zvuku na škále od 0 po 100
volume                                     sila prehrávania zvuku na škále od 0 po 100
web_screen                                 ak je False, neposiela sa grafický výstup na monitor
instr                                      inštrukcie pre exponát
info                                       key-value hodnoty pre info html screen, pre názornú ukážku pozri napr. time_score_info 
score_line_1                               text, ktorý sa zobrazí pred výsledným score
score_line_2                               text, ktorý sa zobrazí za výsledným score
max_score_format                           formát, v ktorom sa zobrazuje score
=========================================  ======

Viaceré exponáty majú okrem vyššie uvedených aj ďalšie nastavenia, ktoré sú pre ne špecifické.

.. csv-table:: 
    :header: "ID exponátu", "názov premennej", "význam"
    :widths: 15, 35, 50

    "82", "threshold", "výkon, pri ktorého prekročení spustí exponát hru"
    "89", "min_random_time (max)", "interval z ktorého sa vyberá náhodné čakanie"
    "89", "lighted_wall_time", "dĺžka svietenia na strane výhercu"
    "98", "lighted_button_time", "konfiguruje dĺžku, počas ktorej je tlačidlo rozsvietené"
    "98", "lighted_buttons", "počet naraz rozsvietených tlačidiel"
    "99", "penalty", "penalta za dotyk"
    "99", "penalty_timeout", "ak po tomto čase hráč nepreruší začatý dotyk s dráhou, dostáva penaltu o
    veľkosti penalty_multiple"
    "99", "second_penalty_multiple", "viď penalty_timeout"
    "101", "activation_time", "čas potrebný pre držanie tlačidla, aby sa toto zaregistrovalo ako
    maximálna výška bez výskoku"
    "101", "jump_time", "v tomto časovom intervale sa stlačené tlačidlá pripisujú k tomu istému
    výskoku"
    "102", "random_time", "konfiguruje dĺžku náhodného čakania"
    "105", "threshold", "hlasitosť na intervale 0-100, pri ktorej exponát spustí meranie"
    "107", "sound_sets", "popisuje sady zvukov, ktoré pexeso využíva"
