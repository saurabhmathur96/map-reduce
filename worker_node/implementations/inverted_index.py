from operator import itemgetter

def mapper(lines):
    document_id = lines[0].strip()
    pairs = [(word, [document_id]) for line in lines[1:] for word in line.split()]
    return sorted(pairs, key=itemgetter(0))

def reducer(pairs):
    result = []
    current_word, current_docs = None, []
    for word, docs in sorted(pairs, key=itemgetter(0)):
        if word == current_word:
            current_docs.extend(docs)
        else:
            if current_word is not None:
                result.append([current_word, list(set(current_docs))])
            current_word = word
            current_docs = docs
    if word == current_word:
        result.append([current_word, list(set(current_docs))])
    return result 
