import re
import sys
import collections


# merges dict2 into dict1
def merge_rules(dict1, dict2):
    for lhs, rules in dict2.items():
        if lhs in dict1:
            for rhs in rules:
                dict1[lhs][rhs] += dict2[lhs][rhs]
        else:
            dict1[lhs] = dict2[lhs]
    return dict1


def get_rules(branch):
    if branch == '':
        return 'err', {}, {}, [], {}
    rr = {}  # rules
    rl = {}  # lexical rules
    v = set()  # words
    n = collections.defaultdict(int)  # notterminals
    # only two symbols left: A v
    leaves = branch.split()
    if len(leaves) == 2:
        # save lexical rule and word

        rl = {
            leaves[0]: collections.defaultdict(int, {
                leaves[1]: 1
            })}
        v.add(leaves[1])
        n[leaves[0]] = 1

        return leaves[0], rl, rr, v, n
    elif len(leaves) < 2:
        print('ERROR: Something went wrong if there is only one symbol left. ', leaves, file=sys.stderr)
        return 'err', {}, {}, [], {}

    # A -> A ...
    root, branches = branch.split(' ', 1)
    n[root] = 1
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
        print('ERROR: The number of opening and closing parentheses does not add up.', file=sys.stderr)
        return 'err', {}, {}, [], {}

    # get next rule
    right_side = []
    for i in range(len(br)):
        # call function for new found branch without the outmost parentheses
        nonterminal, rulesl, rulesr, words, nonterminals = get_rules(br[i][1:len(br[i]) - 1])
        # don't use illegal tree for the grammar
        if nonterminal == 'err':
            return 'err', {}, {}, [], {}
        right_side.append(nonterminal)
        # save rules and words from lower branches
        rl = merge_rules(rl, rulesl)
        rr = merge_rules(rr, rulesr)
        v.update(words)
        for nt in nonterminals:
            n[nt] += nonterminals[nt]
    right_side = tuple(right_side)

    # add new rule
    rule = {
        root: collections.defaultdict(int, {
            right_side: 1
        })
    }
    rr = merge_rules(rr, rule)

    return root, rl, rr, v, n


def pre_check(tree):
    # check if we even need to take a look at it
    opening = re.findall(r'\(', tree)
    closing = re.findall(r'\)', tree)
    if len(opening) != len(closing):
        print('ERROR: The number of opening and closing parentheses does not add up.', file=sys.stderr)
        return ''

    # ignore everything before the first opening parenthesis
    i = 0
    while tree[i] != '(':
        i = i + 1
    tree = tree[i:len(tree)]

    # insert and or remove white spaces
    problems = re.findall(r'(\w|\))\(', tree)
    for combo in problems:
        if (combo[0]) == ')':
            rex = r'\)\('
        else:
            rex = combo[0] + r'\('
        tree = re.sub(rex, combo[0] + ' (', tree)
    tree = re.sub(r' +', ' ', tree)
    tree = re.sub(r'\( ', '(', tree)
    tree = re.sub(r' \)', ')', tree)

    return tree


def induce_grammar(name):
    s = ''  # start symbol
    rr = {}  # rules
    rl = {}  # lexical rules
    v = set()  # words
    n = collections.defaultdict(int)  # notterminals
    # iterate over all training data
    for tree in sys.stdin:
        tree = pre_check(tree)
        if tree == '':
            continue

        root, rulesl, rulesr, words, nonterminals = get_rules(tree[1:len(tree) - 2])

        if root == 'err':
            continue

        if s != '':
            if s != root:
                print('ERROR: start symbol changed from ', s, ' to ', root, file=sys.stderr)
                # don't use this tree
                continue
        else:
            s = root

        # add rules and symbols to grammar
        rr = merge_rules(rr, rulesr)
        rl = merge_rules(rl, rulesl)
        v.update(words)
        for nt in nonterminals:
            n[nt] += nonterminals[nt]

    w = sorted(v)

    # calculate probabilities and write to stdout
    if name == '':
        for lhs, rules in rr.items():
            for rhs in rules:
                rr[lhs][rhs] = rr[lhs][rhs] / n[lhs]
                if rr[lhs][rhs] % 1 > 0:
                    print(lhs, '->', *rhs, rr[lhs][rhs])
                else:
                    print(lhs, '->', *rhs, "{:d}".format(int(rr[lhs][rhs])))

        for lhs, rules in rl.items():
            for rhs in rules:
                rl[lhs][rhs] = rl[lhs][rhs] / n[lhs]
                if rl[lhs][rhs] % 1 > 0:
                    print(lhs, rhs, rl[lhs][rhs])
                else:
                    print(lhs, rhs, "{:d}".format(int(rl[lhs][rhs])))

        for word in w:
            print(word)
    # calculate probabilities and save data in files
    else:
        f = open(name + '.rules', "w")
        for lhs, rules in rr.items():
            for rhs in rules:
                rr[lhs][rhs] = rr[lhs][rhs] / n[lhs]
                if rr[lhs][rhs] % 1 > 0:
                    f.write(lhs + ' -> ' + ' '.join(map(str, rhs)) + ' ' + str(rr[lhs][rhs]) + '\n')
                else:
                    f.write(
                        lhs + ' -> ' + ' '.join(map(str, rhs)) + ' ' + "{:d}".format(int(rr[lhs][rhs])) + '\n')
        f.close()

        f = open(name + '.lexicon', "w")
        for lhs, rules in rl.items():
            for rhs in rules:
                rl[lhs][rhs] = rl[lhs][rhs] / n[lhs]
                if rl[lhs][rhs] % 1 > 0:
                    f.write(lhs + ' ' + str(rhs) + ' ' + str(rl[lhs][rhs]) + '\n')
                else:
                    f.write(lhs + ' ' + str(rhs) + ' ' + "{:d}".format(int(rl[lhs][rhs])) + '\n')
        f.close()

        f = open(name + '.words', "w")
        for word in w:
            f.write(word + '\n')
        f.close()
