import sys


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
                word = tree[last_space:i + 1]
                if word in count:
                    count[word] += 1
                else:
                    count[word] = 1

#    last_space = -1
#    i = 0
#    while i < len(corpus):
#        if corpus[i] == ' ':
#            last_space = i
#        elif corpus[i] == ')' and corpus[i - 1] != ')':
#            word = corpus[last_space:i + 1]
#            if count[word] <= threshold:
#                corpus = corpus[:last_space + 1] + 'UNK' + corpus[i:]
#                i = last_space + 4
#        i += 1

    for word, frequency in count.items():
        if frequency <= threshold:
            corpus = corpus.replace(word, ' ' + 'UNK' + ')')

    print(corpus, end = "")
