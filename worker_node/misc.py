import json

def save_to_file(filename, data):
    with open(filename, "w") as handle:
        json.dump(data, handle)
    
def read_from_file(filename):
    with open(filename, "r") as handle:
        return json.load(handle)


def hash_function(s):
    # maps from strings to integer
    return sum(ord(c) for c in s)