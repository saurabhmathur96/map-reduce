from collections import namedtuple

Job = namedtuple("Job", ["id", 
                          "name",  
                          "input_dir", 
                          "output_dir", 
                          "status", # "submitted", "complete", "aborted"
                          "mappers_file",
                          "reducers_file",
                          "created_on"])

class JobCollection(object):
    def __init__(self, db):
        self.db = db
        self._create_table()
    
    def _create_table(self):
        cursor = self.db.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS jobs(
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          name TEXT,
                          input_dir TEXT,
                          output_dir TEXT,
                          status TEXT,
                          mappers_file TEXT,
                          reducers_file TEXT,
                          created_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL)""")
        self.db.commit()
    
    def add(self, task):
        cursor = self.db.cursor()
        values = [task.name, task.input_dir, task.output_dir, task.status, 
                  task.mappers_file, task.reducers_file]
        cursor.execute("""INSERT INTO jobs
                          (name, input_dir, output_dir, status, 
                          mappers_file, reducers_file) 

                          VALUES (?, ?, ?, ?, ?, ?)""", 
                        values)
        self.db.commit()
        return cursor.lastrowid
    
    def update_by_id(self, id, update_parameters):
        cursor = self.db.cursor()
        keys, values = zip(*update_parameters.items())
        update = ", ".join("%s = ?" % k for k in keys)
        query = "UPDATE jobs SET %s WHERE id=?" % update
        cursor.execute(query, values)
        self.db.commit()
    
    def find_by_id(self, id):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM jobs WHERE id=?", [id])
        job_row = cursor.fetchone()
        return Job(*job_row) if job_row is not None else None
    
    def find_one(self, query_parameters=None):
        cursor = self.db.cursor()
        if query_parameters is None:
            cursor.execute("SELECT * FROM jobs ORDER BY created_on ASC LIMIT 1")
        else:
            keys, values = zip(*query_parameters.items())
            condition = " AND ".join("%s = ?" % k for k in keys)
            query = "SELECT * FROM jobs WHERE %s ORDER BY created_on ASC LIMIT 1" % condition
            cursor.execute(query, values)
        job_row = cursor.fetchone()
        
        return Job(*job_row) if job_row is not None else None

    def count(self, query_parameters=None):
        cursor = self.db.cursor()
        if query_parameters is None:
            cursor.execute("SELECT COUNT(*) FROM jobs")
        else:
            keys, values = zip(*query_parameters.items())
            condition = "".join("%s = ?" % k for k in keys)
            query = "SELECT COUNT(*) FROM jobs where %s" % condition
            cursor.execute(query, values)
        count, *_ = cursor.fetchone()
        return count