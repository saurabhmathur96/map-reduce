import glob
import os, signal
from os import path
from shutil import rmtree

for dirname in glob.glob("worker_directory*"):
    pidfile = path.join(dirname, "rpc_server.pid")
    try:
        pid = open(pidfile).read().strip()
        print ("%s: Killing pid %s" % (dirname, pid))
        os.kill(int(pid), signal.SIGTERM)
       
    except OSError:
        pass

    pidfile = path.join(dirname, "worker_daemon.pid")
    try:
        pid = open(pidfile).read().strip()
        print ("%s: Killing pid %s" % (dirname, pid))
        os.kill(int(pid), signal.SIGTERM)
        
    except OSError:
        pass

    
    print ("%s: Deleting directory" % dirname)
    try:
        rmtree(dirname)
    except OSError:
        pass