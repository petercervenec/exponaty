import os
import sys
import pstats
import gprof2dot

expo_num=sys.argv[1]
filename = '/home/marcelka/projects/expo/profile/profile-expo-'+expo_num

#p = pstats.Stats(filename)
#p.strip_dirs().sort_stats(2).print_stats()

#os.system('gprof2dot -f pstats ' + filename + ' | dot -Tpng -o ' + filename + '.png')
os.system('python2 gprof2dot.py -f pstats ' + filename + ' | dot -Tpng -o ' + filename + '.png')
os.system('eog ' + filename + '.png &')
