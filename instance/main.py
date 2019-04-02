import os
import sys


def launch_instance(filename, TOKEN, APIKEY):
    my_dir = os.path.dirname(sys.argv[0])
    os.system('%s %s %s %s' % (sys.executable,
                               os.path.join(my_dir + '/instance', filename),
                               TOKEN, APIKEY))