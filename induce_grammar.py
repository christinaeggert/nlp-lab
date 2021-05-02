from collections import Counter
import sys

def get_rules(branch):
    rl = []
    rr = []
    v = set()
    n = []
    # only two symbols left: A v
    leafs = branch.split()
    if len(leafs) == 2:
        # save lexical rule and word
        rl.append(leafs[0] + ' ' + leafs[1])
        v.add(leafs[1])
        n.append(leafs[0])

        return leafs[0], rl, rr, v, n
    elif len(leafs) < 2:
        print('ERROR: Something went wrong if there is only one symbol left.')
        exit(1)

    # A -> A ...
    root, branches = branch.split(' ', 1)
    n.append(root)
    # find the branches by matching parentheses
    opening = 0
    closing = 0
    cut = 0
    br = []
    for i in range(len(branches)):
        if branches[i] == '(':
            opening = opening + 1
        elif branches[i] == ')':
            closing = closing + 1
            if closing == opening:
                br.append(branches[cut:i + 1])
                cut = i + 2

    # get next rule
    rule = root + ' ->'
    for i in range(len(br)):
        # call function for new found branch without the outmost parentheses
        notterminal, rulesl, rulesr, words, notterminals = get_rules(br[i][1:len(br[i]) - 1])
        rule = rule + ' ' + notterminal
        # save rules and words from lower branches
        rl = rl + rulesl
        rr = rr + rulesr
        v.update(words)
        n = n + notterminals

    # add new rule
    rr.append(rule)

    return root, rl, rr, v, n


def induce_grammar(file, name):
    s = ''  # start symbol
    rr = []  # rules
    rl = []  # lexical rules
    v = set()  # words
    n = []  # notterminals
    # import data from file
    f = open(file)
    line = 1
    lines = len(f.readlines())
    f.close()
    for tree in open(file):
        root, rulesl, rulesr, words, notterminals = get_rules(tree[1:len(tree) - 2])

        if s != '':
            if s != root:
                print('ERROR: start symbol changed from ', s, ' to ', root)
                exit(1)
        else:
            s = root

        rr = rr + rulesr
        rl = rl + rulesl
        v.update(words)
        n = n + notterminals
        print(line, '/', lines, ' trees', end="\r")
        line = line + 1

    nrr = Counter(rr)
    nrl = Counter(rl)
    nn = Counter(n)
    w = sorted(v)

    # calculate probabilities and save data in files
    f = open('output/' + name + '.rules', "w")
    for key in nrr:
        root, rest = key.split(' ', 1)
        f.write(key + ' ' + str(nrr[key] / nn[root]) + '\n')
    f.close()

    f = open('output/' + name + '.lexicon', "w")
    for key in nrl:
        root, rest = key.split(' ', 1)
        f.write(key + ' ' + str(nrl[key] / nn[root]) + '\n')
    f.close()

    f = open('output/' + name + '.words', "w")
    for word in w:
        f.write(word + '\n')
    f.close()
