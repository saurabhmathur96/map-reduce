from xmlrpc.client import ServerProxy
from os import listdir, path, makedirs
from database import Job, JobCollection
import json
import time
import sqlite3

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("name", type=str, help="job name (values supported: word_count, inverted_index)")
    parser.add_argument("input_path", type=str, help="path to a directory having files such that each file is input to a mapper")
    parser.add_argument("output_path", type=str, help="path to output directory")
    parser.add_argument("workers", nargs="+", help="worker addresses")
    args = parser.parse_args()

    assert(len(args.workers) > 1)
    
    makedirs("jobs", exist_ok=True)
    makedirs(args.output_path, exist_ok=True)
    
    dbpath = path.join("jobs", "local.db")
    db = sqlite3.connect(dbpath)
    jobs = JobCollection(db)
    
    
    n_workers = len(args.workers)
    mapper_addresses, reducer_addresses = args.workers[n_workers//2:], args.workers[:n_workers//2]
    # mapper_addresses = reducer_addresses = args.workers
    mapper_data = []
    for i, filename in enumerate(listdir(args.input_path)):
        filepath = path.join(args.input_path, filename)
        input_data = open(filepath).read().splitlines()
        
        address = mapper_addresses[ i % len(mapper_addresses) ]
        address = "http://%s" % address
        
        client = ServerProxy(address)
        task_id = client.submit_task(args.name, "map", input_data)
        mapper_data.append(dict(
            task_id=task_id,
            address=address
        ))
    
    reducer_data = []
    for i, address in enumerate(reducer_addresses):
        address = "http://%s" % address
        client = ServerProxy(address)
        filter_parameters = [i, len(reducer_addresses)]
        task_id = client.submit_task(args.name, "reduce", dict(mappers=mapper_data, filter_parameters=filter_parameters))
        reducer_data.append(dict(
            task_id=task_id,
            address=address,
            filter_parameters=filter_parameters
        ))
    
    now = str(time.time())

    mappers_file = path.join("jobs", "mappers.%s.%s.json" % (args.name, now))
    json.dump(mapper_data, open(mappers_file, "w"))

    reducers_file = path.join("jobs", "reducers.%s.%s.json" % (args.name, now))
    json.dump(reducer_data, open(reducers_file, "w"))

    id = jobs.add(Job(id=None, name=args.name, input_dir=args.input_path, output_dir=args.output_path, status="submitted", mappers_file=mappers_file, reducers_file=reducers_file, created_on=None))

    print (id)
