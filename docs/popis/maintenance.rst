Údržba
******

Pri servisovaní systému je vhodné zvládnuť základné úkony s exponátmi.

získanie konzoly
================
K exponátu treba pripojiť myš, klávesnicu (v prípade, že je to potrebné treba použiť USB hub) a
monitor. Následne po štarte (pozor, boot process trvá niekoľko minút) treba ukončiť beh exponátu (je
to len normálna aplikácia pustená na fullscreen) a k dispozícii je štandardné linuxovské prostredie.
V systéme existujú užívatelia ``root`` a ``pi``, obidvaja majú heslo ``pi``. 

Aktualizácia zdrojových kódov
=============================
v prípade, že by došlo k úprave kódu exponátov, je tento kód možné nahrať priamo na exponát bez
výroby novej SD karty. V domovskom adresári užívateľa ``pi`` sa nachádza git repozitár expo. Do
tohto repozitáru je potrebné pull-núť nové zmeny pomocou príkazu ``git pull``. Heslo, ktorý si
následne systém vypýta je ``expo``. Pozor, na tento úkon je potrebné, aby exponát bol pripojený na
internet.

Root na serveri
===============
Heslo pre používateľa root je ``exponatykosice``

Rozširovanie funkcionality exponátov
====================================
Existujúci kód je spravený v jazyku Python 2.7. 

Jednoduché úpravy v exponátoch sa dajú docieliť zmenou nastavení, html šablón alebo CSS štýlov. 

Pre komplikovanejšie zásahy ako napr. vývoj nového exponátu odporúčam najskôr nainštalovať tento kód
na vývojarovom počítači a hru vyvíjať v spravenom emulátore. Tento sa spustí pomocou príkazu
``python2 start_menu.py emulator``. Pre tento krok je potrebné stiahnuť viacero knižníc, ktoré sa
dajú identifikovať podľa importovaných packages (najprimitívnejšia technika je spúšťať aplikáciu a
inštalovať závislosti, až kým sa aplikácia nerozbehne). Následne je možné dať sa do vývoja exponátu
spôsobom ktorý je analogický k už spraveným exponátom.

Menenie web-stránky zobrazujúcej exponáty na servri
===================================================

  - fotka exponátu sa nahráva v projektovom adresári do podadresára ``static/img/exponates_img/{name}.png`` kde ``name``
    meno exponátu
  - popis exponátu sa čerpá z databázy. Pripojiť sa k nej dá pomocou príkazu ``sqlite3 Museum.db``,
    údaje o exponátoch sú v tabuľke ``exponat``


Rozširovanie funkcionality servra
=================================
Situácia je analogická ako pri exponátoch. Server je spravený v jazyku Python 3.3 a frameworku
Pyramid, pre základné úpravy stačí meniť ``.css`` a ``.mako`` súbory (mako sú šablóny pre html).
Medzi jednoduché zásahy tiež patrí zmena nastavení v súbore ``production.ini`` (pozor, vyžaduje
reštart apache, ktorý aplikáciu servuje). Pre komplikovanejšie úpravy odkazujeme čitateľa na vynikajúcu dokumentáciu k frameworku, nakoľko sa
jedná o veľmi štandardnú aplikáciu v tomto systéme. 




