.. _misc:

Rôzne
*****

Výroba SD-karty "from scratch"
==============================

na SD kartu je potrebné nahrať operačný systém Raspbian. Na ten je potrebné nainštalovať balíčky,
ktoré sú v súčasnosti nainštalované na dodanej SD-karte, ich presný zoznam je možné získať pomocou
príkazu ``dpkg --get-selections``. Ďalej je potrebné nahrať na kartu zdrojový kód exponátov, zabezpečiť, aby sa tento
púšťal po štarte, postarať sa o silent-boot a vypnúť screensaver. 

O automatické spúšťanie sa stará ``autostart`` uložený v ``pi/.config/lxsession/LXDE/autostart``,
ktorého úlohou je púšťať skript ``/home/pi/run_application``; úlohou je ukončiť silent-boot a
spustiť samotný exponát (vo fullscreen móde). Samotný silent boot sa zapína skriptom uloženým v
zložke ``pi/expo/silent_boot``. Pre vypnutie screensavera, treba sledovať návody nájditeľné na
internete.

Logika adresárovej štruktúry v projekte
=======================================

Okrem samotného adresára ``pkg`` obsahujúceho kód exponátov, sa v projekte nachádza viacero
adresárov a súborov, význam dôležitejších z nich je nasledovný: 

.. csv-table:: 
    :header: "adresár/súbor",  "význam"
    :widths: 20, 80

    "arduino", "skript na čítanie dát z arduina potrebný pre exponát bicykel"
    "audio_playing", "pokusné skripty určené hlavne na debugovanie problémov so zvukom"
    "audio_recording", "pokusné skripty určené hlavne na debugovanie problémov so zvukom"
    "barcode", "skripty určené na prácu s qr-scannerom"
    "docs", "dokumentácia, zdrojáky pre tento dokument"
    "expo.db", "databáza, do ktorej sa ukladá voľba exponátu a levelu" 
    "expo.log", "log behu exponátu"
    "main.css", "css pre obrazovky exponátov"
    "rpi_stuff", "pokusné kusy kódu, nie potrebné pre beh exponátu"
    "silent_boot", "skript zapínajúci/vypínajúci screen"
    "start_expo.py", "skript púšťajúci daný exponát"
    "start_menu.py", "skript púšťajúci menu výberu exponátov"
