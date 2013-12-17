Firmware
~~~~~~~~
firmware staci nahrat len raz. Aj medzi vypadkami el. si arduino pamata program.
firmware co tu je bol upraveny. Bol mu rozsireny reset, aby vzdy po prikaze reset sa uviedol do pociatocneho stavu (nie len mode ale aj running a hodnota)


Instalacia FW
~~~~~~~~~~~~~
(ref: http://www.recantha.co.uk/blog/?p=1103)

na nejakom stroji treba arduino. V pripade raspberry balik
arduino-mk
alebo aspon balik
arduino-core

dalej baliky (raspberry pi)

sudo aptitude install picocom
sudo aptitude install python-pip
sudo easy-install configobj
sudo easy-install jinja2
sudo easy_install ino


ino init
nahrat do src subor sketch.ino
ino build
ino upload


ino serial
alebo
/usr/bin/picocom /dev/ttyACM0 -b 9600 -l
robia komunikacia, resp. vypis.

staci aj pouzit
start.sh, ktory vyresetuje zariadenie a na stdout potom idu hodnoty.
prikazy ktore nastavia arduino su ako prvy riadok skriptu, druhy uz robi vypis.
Zoznam prikazov pre arduino je potom v sketch.ino (hore)
