import sqlite3
import importlib
import time
from xmlrpc.client import ServerProxy
from database import TaskCollection
from misc import save_to_file, read_from_file
from daemon import daemon
import operator

class WorkerDaemon(daemon):
    def __init__(self, pidfile, outfile, rootpath, id, task_collection, implementations):
        super().__init__(pidfile, outfile, rootpath)
        self.id = id
        self.task_collection = task_collection
        self.implementations = implementations

    def run_map_task(self, name, input_arguments):
        print ("Running map task %s" % name)
        
        implementation = self.implementations.get(name)
    
        return implementation.mapper(input_arguments)
    
    def run_reduce_task(self, name, input_arguments):
        # input_arguments is a set of addresses to mappers
        # the mappers will be polled for data
        print ("Running reduce task %s" % name)
        results = []
        mappers = input_arguments.get("mappers")
        filter_parameters = input_arguments.get("filter_parameters")
        while len(mappers) != 0:
            retry = []
            for mapper in mappers:
                address, task_id = mapper.get("address"), mapper.get("task_id")
                client = ServerProxy(address, allow_none=True)
                response = client.get_result(task_id, filter_parameters)
                
                if response is not None:
                    print (response)
                    results.extend(response)
                else:
                    retry.append(dict(address=address, task_id=task_id))

            mappers = retry
        
        implementation = self.implementations.get(name)
        return implementation.reducer(results)

    def run(self):
        while True:
            # poll db
            task = self.task_collection.find_one({ "is_complete": 0 })
            if task is None:
                # if there are no remaining tasks, then sleep
                time.sleep(5)
                continue
        
            input_arguments = read_from_file(task.input_file)
            if task.kind == 'map':
                result = sorted(self.run_map_task(task.name, input_arguments), key=operator.itemgetter(0))
            else: 
                result = self.run_reduce_task(task.name, input_arguments)
            save_to_file(task.output_file, result)
            self.task_collection.update_by_id(task.id, { "is_complete": 1 })


import sqlite3

def start(id, rootpath, outfile, pidfile, dbpath, implementations):
    # implementations: dict(name(str) -> module)
    # module must have two functions mapper and reducer
    db = sqlite3.connect(dbpath)
    tasks = TaskCollection(db)
    worker = WorkerDaemon(pidfile, outfile, rootpath, id=id, task_collection=tasks, implementations=implementations)
    print ("Started worker daemon")
    worker.start()
   



if __name__ == "__main__":

    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("id", type=int, help="node id")
    parser.add_argument("rootpath", type=str, help="rootpath")
    parser.add_argument("outfile", type=str, help="outfile")
    parser.add_argument("pidfile", type=str, help="path to daemon pid file")
    parser.add_argument("dbpath", type=str, help="path to sqlite db file")
    args = parser.parse_args()
    id = args.id
    rootpath = args.rootpath
    outfile = args.outfile
    pidfile = args.pidfile
    dbpath = args.dbpath


    #
    # Import new implementations here
    #
    from implementations import word_count, inverted_index

    
    start(id, rootpath, outfile, pidfile, dbpath, { "word_count": word_count, "inverted_index": inverted_index })
    
    
        
