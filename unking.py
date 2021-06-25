import sys
import re


def get_signature(word, i):
    if len(word) == 0:
        return 'UNK'

    letter = '-S'
    if word[0].isupper() and not re.search(r'[a-z]', word):
        letter = '-AC'
    elif word[0].isupper() and i == 1:
        letter = '-SC'
    elif word[0].isupper():
        letter = '-C'
    elif re.search(r'[a-z]', word):
        letter = '-L'
    elif re.search(r'[a-zA-Z]', word):
        letter = '-U'

    number = ''
    if word.isdigit():
        number = '-N'
    elif re.search(r'[0-9]', word):
        number = '-n'

    dash = ''
    if re.search(r'-', word):
        dash = '-H'

    period = ''
    if '.' in word:
        period = '-P'

    comma = ''
    if ',' in word:
        comma = '-C'

    wordsuffix = ''
    if len(word) > 3 and word[len(word) - 1].isalpha():
        wordsuffix = word[:len(word) - 1] + word[len(word) - 1].lower()

    return 'UNK' + letter + number + dash + period + comma + wordsuffix


def unk(threshold):
    corpus = ''
    count = {}
    last_space = -1
    for tree in sys.stdin:
        corpus += tree
        # symbols right before ) are words
        for i in range(len(tree)):
            if tree[i] == ' ':
                last_space = i
            elif tree[i] == ')' and tree[i - 1] != ')':
                word = tree[last_space + 1:i]
                if word in count:
                    count[word] += 1
                else:
                    count[word] = 1

    last_space = -1
    i = 0
    w = 0
    while i < len(corpus):
        if corpus[i] == ' ':
            last_space = i
        elif corpus[i] == '\n':
            w = 0
        elif corpus[i] == ')' and corpus[i - 1] != ')':
            word = corpus[last_space + 1:i]
            w += 1
            if count[word] <= threshold:
                corpus = corpus[:last_space + 1] + 'UNK' + corpus[i:]
                i = last_space + 4
                # signed_unk = get_signature(word, w)
                # corpus = corpus[:last_space + 1] + signed_unk + corpus[i:]
                # i = last_space + 1 + len(signed_unk)
        i += 1

    # for word, frequency in count.items():
    #    if frequency <= threshold:
    #        corpus = corpus.replace(word, ' ' + 'UNK' + ')')

    print(corpus, end="")
