from collections import namedtuple

Task = namedtuple("Task", ["id",
                           "name", 
                           "kind", 
                           "is_complete", 
                           "input_file", 
                           "output_file",
                           "created_on"])

class TaskCollection(object):
    def __init__(self, db):
        self.db = db
        self._create_table()
    
    def _create_table(self):
        cursor = self.db.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS tasks(
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          name TEXT,
                          kind TEXT,
                          is_complete INTEGER,
                          input_file TEXT,
                          output_file TEXT,
                          created_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL)""")
        self.db.commit()
    
    def add(self, task):
        cursor = self.db.cursor()
        values = [task.name, task.kind, task.is_complete, 
                  task.input_file, task.output_file]
        cursor.execute("""INSERT INTO tasks
                          (name, kind, is_complete, 
                          input_file, output_file) 

                          VALUES (?, ?, ?, ?, ?)""", 
                        values)
        self.db.commit()
        return cursor.lastrowid
    
    def update_by_id(self, id, update_parameters):
        cursor = self.db.cursor()
        keys, values = zip(*update_parameters.items())
        update = ", ".join("%s = ?" % k for k in keys)
        query = "UPDATE tasks SET %s WHERE id=?" % update
        values = (*values, id)
        cursor.execute(query, values)
        self.db.commit()
    
    def find_by_id(self, id):
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id=?", [id])
        task_row = cursor.fetchone()
        return Task(*task_row) if task_row is not None else None
    
    def find_one(self, query_parameters=None):
        cursor = self.db.cursor()
        if query_parameters is None:
            cursor.execute("SELECT * FROM tasks ORDER BY created_on ASC LIMIT 1")
        else:
            keys, values = zip(*query_parameters.items())
            condition = " AND ".join("%s = ?" % k for k in keys)
            query = "SELECT * FROM tasks WHERE %s ORDER BY created_on ASC LIMIT 1" % condition
            cursor.execute(query, values)
        task_row = cursor.fetchone()
        
        return Task(*task_row) if task_row is not None else None

    def count(self, query_parameters=None):
        cursor = self.db.cursor()
        if query_parameters is None:
            cursor.execute("SELECT COUNT(*) FROM tasks")
        else:
            keys, values = zip(*query_parameters.items())
            condition = "".join("%s = ?" % k for k in keys)
            query = "SELECT COUNT(*) FROM tasks where %s" % condition
            cursor.execute(query, values)
        count, *_ = cursor.fetchone()
        return count


if __name__ == "__main__":
    import sqlite3

    db = sqlite3.connect(":memory:")
    tasks = TaskCollection(db)
    task = Task(id=None, created_on=None, name="wordcount", kind="map", is_complete=False, input_file="A.txt", output_file="B.txt")
    tasks.add(task)

    task = Task(id=None, created_on=None, name="wordcount", kind="reduce", is_complete=False, input_file="B.txt", output_file="C.txt")
    tasks.add(task)

    print (tasks.find_by_id(10))
    print (tasks.count())
    print (tasks.find_one())