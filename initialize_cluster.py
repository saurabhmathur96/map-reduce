import argparse
from os import path
import os
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("addresses", nargs="+", help="addresses of worker nodes (ip_address:port)")
args = parser.parse_args()


for id, address in enumerate(args.addresses):
    rootpath = path.abspath("worker_directory_%s" % id)
    os.makedirs(rootpath,exist_ok=True)

    dbpath = path.join(rootpath, "local.db")

    outfile = path.join(rootpath, "rpc_server.log")
    pidfile = path.join(rootpath, "rpc_server.pid")
    exec_path = path.join("worker_node", "rpc_server.py")
    args = [str(id), rootpath, outfile, pidfile, dbpath, address]
    subprocess.call(["python3", exec_path, *args])
    
    pidfile = path.join(rootpath, "worker_daemon.pid")
    outfile = path.join(rootpath, "worker_daemon.log")
    exec_path = path.join("worker_node", "worker_daemon.py")
    args = [str(id), rootpath, outfile, pidfile, dbpath]
    subprocess.call(["python3", exec_path, *args])