from xmlrpc.client import ServerProxy
from os import listdir, path, makedirs
from database import Job, JobCollection
import json
import sqlite3
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("job_id", type=int, help="job id")
args = parser.parse_args()

job_id = args.job_id
dbpath = path.join("jobs", "local.db")
db = sqlite3.connect(dbpath)
jobs = JobCollection(db)
job = jobs.find_by_id(job_id)

reducers = json.load(open(job.reducers_file))

result = []
for reducer in reducers:
    address = reducer.get("address")
    task_id = reducer.get("task_id")
    client = ServerProxy(address, allow_none=True)
    response = client.get_result(task_id)
    while response is None:
        try:
            client = ServerProxy(address, allow_none=True)
            response = client.get_result(task_id)
        except ConnectionError:
            # restart
            print ("One or more workers failed. Please re-run job")
            exit()
    if response == 0:
        # restart
        print ("One or more workers failed. Please re-run job")
        exit()
    result.extend(response)


makedirs(job.output_dir, exist_ok=True)

from time import time
with open(path.join(job.output_dir, "job.%s.%s.json" % (job.id, str(time()))), "w") as outfile:
    json.dump(result, outfile)
# c = [c for w,c in result]
# print (sum(c))