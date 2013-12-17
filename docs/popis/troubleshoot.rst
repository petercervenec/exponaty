.. _troubleshoot:
Troubleshoot
************

Možné zádrhele pri spustení
===========================
Pri spustení sa treba uistiť, či všetky hardware komponenty exponátu sú správne zapojené. Treba tiež
skontrolovať príslušné periférie, bez ktorých niektoré exponáty nemusia nabehnúť.

Korektné zapojenie expanderových dosiek treba skontrolovať príkazom ``sudo y2cdetect -y 1``

Špeciálny dôraz treba dať na to, aby v exponáte boli správne expandery zapojené na správnych miestach.
Dôležité je tiež dohliadnuť na to, aby interrupt jumpers boli nasadené na správnych dvojiciach
pin-headers (toto sa môže pokaziť najmä pri výmene niektorého kusu hardware).

Pokiaľ RPi odmieta bootovať (svieti iba červená kontrolka a zelená je počas celého času úplne neaktívna), je potrebné spraviť reset.

Možné zádrhele pri hre
======================

Pokiaľ ani reset systému problémy nevyrieši, treba kontaktovať podporu.

Server
=========

Uistite sa, či exponát je riadne zapojený do servera, či dostal od neho IP adresu a či funguje ping. Pokiaľ problémy
pretrvávajú, kontaktujte podporu.



