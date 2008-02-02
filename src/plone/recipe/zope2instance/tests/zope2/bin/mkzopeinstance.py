# fake mkzopeinstance, that creates a minimal
# structure for the recipe to get happy
import sys
import os

dir_ = sys.argv[-3]
os.mkdir(dir_)
os.mkdir(os.path.join(dir_, 'etc'))
os.mkdir(os.path.join(dir_, 'bin'))

for file_ in ('runzope', 'zopectl', 'runzope.bat', 'zopeservice.py'):
    f = open(os.path.join(dir_, 'bin', file_), 'w')
    f.write("#")
    f.close()

