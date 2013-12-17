Inštalácia
**********

Exponáty
========

Dodaný kód je možné inštalovať iba na špecifický hardware, určený pre daný exponát. Inštalácia sa
deje nakopírovaním dodaného image SD karty na novú SD kartu a jej následným vsunutím do Raspberry Pi (RPi); po
reštartovaní systému by mal exponát správne nabehnúť. 

Pokiaľ chce užívateľ dostať do funkčného stavu aj web-kameru (a s ňou spojené prihlasovanie
používateľov) monitor a zber dát na serveri, je potrebné:

        - pripojiť spomínané periférie do RPi
        - v prípade, že RPi má nedostatok USB portov alebo elektrického výkonu v nich, treba použiť
          napájací USB hub
        - zapnúť zber kódov v konfiguračnom súbore 
        - zabezpečiť pripojenie exponátu k serveru pomocou ethernetového kábla a switch
        - reštartovať exponát

Po týchto operáciách exponát funguje využívajúc možnosti registrácie, zberu dát a zobrazovania
výstupov na pripojenom monitore. Pokiaľ niečo nefunguje, pozrite troubleshoot_

Server
======

Inštalácia
----------

Na strane servera sa nachádza aplikácia napísaná v jazyku Python3 a frameworku Pyramid. O perzistenciu dát sa stará
databáza SQLite, samotným serverom je Apache s nainštalvaným mod_wsgi, ktorý servuje generickú
Python web-aplikáciu. 

Pre samotnú inštaláciu je potrebné na server nainštalovať všetky potrebné balíčky, ktorých zoznam sa
dá zistiť príkazom ``dpkg --get-selections``. Ďalej, na server je potrebné z dodaného repozitára
nahrať aplikáciu (nižšie), nainštalovať ju a spojazdniť ju napísaním správneho konfiguračného súboru (pozri priečinok
``/etc/apache2``). 

Inštalácia aplikácie sa robí presne podľa návodu na stránkach
http://docs.pylonsproject.org/projects/pyramid/en/1.4-branch/narr/install.html 
(všeobecný návod), a 
http://docs.pylonsproject.org/projects/pyramid/en/1.0-branch/tutorials/modwsgi/index.html
(špeciálne pre spoluprácu s ``mod_wsgi``). Pri inštalácii neslobodno odignorovať pasáž o vytcorení
virtuálneho prostredia pomocou ``virtualenv``; dobré je tiež pamätať, že pri modifikácii už
nainštalovanej aplikácie, treba túto aplikáciu po každej zmene znovunainštalovať.

Server má dve sieťové rozhrania eth0 je to, ktorým server komunikuje s vonkajším svetom, eth1 je určené
na komunikáciu s exponátmi. 

Po inštalácii servera je potrebné pre bezproblémovú komunikáciu so servrom splniť nasledovné:

        - exponáty musia byť pripojené ethernetovým káblom na server
        - exponáty si musia pýtať IP adresu pomocou DHCP a server im musí byť vedieť adresu prideliť
        - server musí odpovedať na ping z exponátov
        - v settings.py je potrebné nastaviť server_url (vyhľadaj tento reťazec). Okrem url je možné
          na tomto mieste špecifikovať aj port, na ktorý sa majú posielať informácie z exponátov.

prideľovanie IP adries a pinganie sa deje automaticky, a figuruje tu hlavne preto, aby sa prípade
nefunkčnosti ľahšie hľadal zdroj chyby.

Webstránka
==========

Web múzea sa stáva aktívnym v okamihu, keď server beží a je napojený na internet. V tomto okamihu
môže hocikto prezerať obsah webu na štandardnom porte 80. Po zakúpení nejakej domény (napr.
exponaty.sk) je potom možné nastaviť ju tak, aby odkazovala na verejnú IP servera; inou možnosťou je
začlenenie servera pod už existujúcu doménu (napr. muzeum.kvant.sk). Pre toto riešenie je potrebné
správne nakonfigurovať web-server obsluhujúci túto doménu.




