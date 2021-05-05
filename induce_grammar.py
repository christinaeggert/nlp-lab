from collections import Counter
import sys


def get_rules(branch):
    if branch == '':
        return 'err', [], [], [], []
    rl = []
    rr = []
    v = set()
    n = []
    # only two symbols left: A v
    leaves = branch.split()
    if len(leaves) == 2:
        # save lexical rule and word
        rl.append(leaves[0] + ' ' + leaves[1])
        v.add(leaves[1])
        n.append(leaves[0])

        return leaves[0], rl, rr, v, n
    elif len(leaves) < 2:
        print('ERROR: Something went wrong if there is only one symbol left. ', leaves)
        return 'err', [], [], [], []

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

    if closing != opening:
        print('ERROR: The number of opening and closing parentheses does not add up.')
        return 'err', [], [], [], []

    # get next rule
    rule = root + ' ->'
    for i in range(len(br)):
        # call function for new found branch without the outmost parentheses
        nonterminal, rulesl, rulesr, words, nonterminals = get_rules(br[i][1:len(br[i]) - 1])
        # don't use illegal tree for the grammar
        if nonterminal == 'err':
            return 'err', [], [], [], []
        rule = rule + ' ' + nonterminal
        # save rules and words from lower branches
        rl = rl + rulesl
        rr = rr + rulesr
        v.update(words)
        n = n + nonterminals

    # add new rule
    rr.append(rule)

    return root, rl, rr, v, n


def induce_grammar(name):
    s = ''  # start symbol
    rr = []  # rules
    rl = []  # lexical rules
    v = set()  # words
    n = []  # notterminals
    # import data from file
    # f = open(file)
    # line = 1
    # lines = len(f.readlines())
    # f.close()
    # iterate over all training data
    for tree in sys.stdin:
        root, rulesl, rulesr, words, notterminals = get_rules(tree[1:len(tree) - 2])

        if root == 'err':
            continue

        if s != '':
            if s != root:
                print('ERROR: start symbol changed from ', s, ' to ', root)
                # don't use this tree
                continue
        else:
            s = root

        # add rules and symbols to grammar
        rr = rr + rulesr
        rl = rl + rulesl
        v.update(words)
        n = n + notterminals
        # print(line, '/', lines, ' trees', end="\r")
        # line = line + 1

    nrr = Counter(rr)
    nrl = Counter(rl)
    nn = Counter(n)
    w = sorted(v)

    # calculate probabilities and write to stdout
    if name == '':
        for key in nrr:
            root, rest = key.split(' ', 1)
            print(key, ' ', str(nrr[key] / nn[root]))

        for key in nrl:
            root, rest = key.split(' ', 1)
            print(key, ' ', str(nrl[key] / nn[root]))

        for word in w:
            print(word)
    # calculate probabilities and save data in files
    else:
        f = open(name + '.rules', "w")
        for key in nrr:
            root, rest = key.split(' ', 1)
            f.write(key + ' ' + str(nrr[key] / nn[root]) + '\n')
        f.close()

        f = open(name + '.lexicon', "w")
        for key in nrl:
            root, rest = key.split(' ', 1)
            f.write(key + ' ' + str(nrl[key] / nn[root]) + '\n')
        f.close()

        f = open(name + '.words', "w")
        for word in w:
            f.write(word + '\n')
        f.close()
