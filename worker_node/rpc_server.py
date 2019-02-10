import sqlite3
import time
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
from misc import save_to_file, read_from_file, hash_function
from database import Task, TaskCollection
from daemon import daemon

class RPCController(object):
    def __init__(self, task_collection):
        self.task_collection = task_collection

    def submit_task(self, name, kind, arguments):
        print ("Received task:", (name, kind))
        now = str(time.time())
        input_file = "input.%s.%s.%s.json" % (name, kind, now)
        output_file =  "output.%s.%s.%s.json" % (name, kind, now)

        save_to_file(input_file, arguments)


        id = self.task_collection.add(
            Task(
                id=None,
                created_on=None,
                name=name,
                kind=kind,
                is_complete=False,
                input_file=input_file,
                output_file=output_file
            )
        )
        return id

        

    def get_result(self, id, filter_parameters=None):
        print ("Received result request for id=%s, filter_parameters=%s" % (id, filter_parameters))
        task = self.task_collection.find_by_id(id)
        if not task.is_complete:
            return None
        
        result = read_from_file(task.output_file)

        if filter_parameters is None:
            return result
        
        filter_id, filter_mod = filter_parameters
        
        return [(key, value) for key, value in result if hash_function(key) % filter_mod == filter_id]


class ServerDaemon(daemon):
    def __init__(self, pidfile, outfile, rootpath, ip_address, port, controller):
        super().__init__(pidfile, outfile, rootpath)
        self.ip_address = ip_address
        self.port = port
        self.controller = controller
    
    def run(self):
        server = SimpleXMLRPCServer((self.ip_address, self.port), allow_none=True)
        server.register_introspection_functions()
        server.register_instance(self.controller)

        print ("Started server at %s:%s" % (self.ip_address, self.port))
        
        server.serve_forever()


import sqlite3
def start(id, outfile, pidfile, rootpath, dbpath, ip_address, port):
    db = sqlite3.connect(dbpath)
    tasks = TaskCollection(db)
    controller = RPCController(tasks)
    server = ServerDaemon(pidfile, outfile, rootpath, ip_address, port, controller)
    server.start()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("id", type=int, help="node id")
    parser.add_argument("rootpath", type=str, help="rootpath")
    parser.add_argument("outfile", type=str, help="outfile")
    parser.add_argument("pidfile", type=str, help="path to daemon pid file")
    parser.add_argument("dbpath", type=str, help="path to sqlite db file")
    parser.add_argument("address", type=str, help="ip_address:port")
    args = parser.parse_args()
    id = args.id
    outfile = args.outfile
    pidfile = args.pidfile
    rootpath = args.rootpath
    dbpath = args.dbpath
    ip_address, port = args.address.split(":")
    start(id, outfile, pidfile,rootpath, dbpath, ip_address, int(port))




    
