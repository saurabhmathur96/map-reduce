from operator import itemgetter
from itertools import groupby
import string


def clean(text):
    translator = str.maketrans('', '', string.punctuation)
    return text.lower().translate(translator)


def mapper(lines):
    pairs = [(word, 1) for line in lines for word in line.split()]
    return sorted(pairs, key=itemgetter(0))


def reducer(pairs):
    result = []
    current_word, current_count = None, 0
    for word, count in sorted(pairs, key=itemgetter(0)):
        if word == current_word:
            current_count += count
        else:
            if current_word is not None:
                result.append([current_word, current_count])
            current_word = word
            current_count = count
    if word == current_word:
        result.append([current_word, current_count])
    return result 


if __name__ == "__main__":
    lines = \
        """All that is gold does not glitter,
Not all those who wander are lost;
The old that is strong does not wither,
Deep roots are not reached by the frost.
From the ashes, a fire shall be woken,
A light from the shadows shall spring;
Renewed shall be blade that was broken,
The crownless again shall be king.""".splitlines()

    mapper_output = mapper(lines)
    print(mapper_output)

    reducer_input = sorted(mapper_output, key=itemgetter(0))
    reducer_output = reducer(reducer_input)
    print(reducer_output)
