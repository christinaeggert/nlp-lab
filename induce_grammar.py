import re
import sys


# merges dict2 into dict1
def merge_rules(dict1, dict2):
    for root in dict2:
        if root in dict1:
            for word in dict2[root]:
                if word in dict1[root]:
                    dict1[root][word] = dict1[root][word] + dict2[root][word]
                else:
                    dict1[root][word] = dict2[root][word]
        else:
            dict1[root] = dict2[root]
    return dict1


def get_rules(branch):
    if branch == '':
        return 'err', {}, {}, [], []
    rr = {}  # rules
    rl = {}  # lexical rules
    v = set()  # words
    # n = []  # notterminals
    # only two symbols left: A v
    leaves = branch.split()
    if len(leaves) == 2:
        # save lexical rule and word
        rl[leaves[0]] = {
            'root_count': 1,
            leaves[1]: 1
        }
        v.add(leaves[1])
        # n.append(leaves[0])  # even necessary anymore?

        return leaves[0], rl, rr, v  # , n
    elif len(leaves) < 2:
        print('ERROR: Something went wrong if there is only one symbol left. ', leaves, file=sys.stderr)
        return 'err', [], [], []  # , []

    # A -> A ...
    root, branches = branch.split(' ', 1)
    # n.append(root)
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
        return 'err', [], [], []  # , []

    # get next rule
    right_side = []
    for i in range(len(br)):
        # call function for new found branch without the outmost parentheses
        nonterminal, rulesl, rulesr, words = get_rules(br[i][1:len(br[i]) - 1])
        # don't use illegal tree for the grammar
        if nonterminal == 'err':
            return 'err', {}, {}, []  # , []
        right_side.append(nonterminal)
        # save rules and words from lower branches
        rl = merge_rules(rl, rulesl)
        rr = merge_rules(rr, rulesr)
        v.update(words)
        # n = n + nonterminals
    right_side = tuple(right_side)

    # add new rule
    rule = {
        root: {
            'root_count': 1,
            right_side: 1
        }
    }
    rr = merge_rules(rr, rule)

    return root, rl, rr, v  # , n


def induce_grammar(name):
    s = ''  # start symbol
    rr = {}  # rules
    rl = {}  # lexical rules
    v = set()  # words
    # n = []  # notterminals
    # iterate over all training data
    for tree in sys.stdin:
        # ignore everything before the first opening parenthesis
        i = 0
        while tree[i] != '(':
            i = i + 1
        tree = tree[i:len(tree)]
        # insert and or remove white spaces
        problems = re.findall(r'\w\(', tree)
        for combo in problems:
            tree = re.sub(combo[0] + r'\(', combo[0] + ' (', tree)
        tree = re.sub(r' +', ' ', tree)
        tree = re.sub(r'\( ', '(', tree)
        tree = re.sub(r' \)', ')', tree)
        root, rulesl, rulesr, words = get_rules(tree[1:len(tree) - 2])

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
        # n = n + notterminals

    w = sorted(v)

    # calculate probabilities and write to stdout
    if name == '':
        for root in rr.keys():
            if root in rl:
                total = rr[root]['root_count'] + rl[root]['root_count']
            else:
                total = rr[root]['root_count']
            for right in rr[root].keys():
                if right == 'root_count':
                    continue

                rr[root][right] = rr[root][right] / total
                if rr[root][right] % 1 > 0:
                    print(root, '->', *right, rr[root][right])
                else:
                    print(root, '->', *right, "{:d}".format(int(rr[root][right])))

        for root in rl.keys():
            if root in rr:
                total = rr[root]['root_count'] + rl[root]['root_count']
            else:
                total = rl[root]['root_count']
            for right in rl[root].keys():
                if right == 'root_count':
                    continue

                rl[root][right] = rl[root][right] / total
                if rl[root][right] % 1 > 0:
                    print(root, right, rl[root][right])
                else:
                    print(root, right, "{:d}".format(int(rl[root][right])))
            if root in rr:
                del rr[root]['root_count']
            del rl[root]['root_count']

        for word in w:
            print(word)
    # calculate probabilities and save data in files
    else:
        f = open(name + '.rules', "w")
        for root in rr.keys():
            if root in rl:
                total = rr[root]['root_count'] + rl[root]['root_count']
            else:
                total = rr[root]['root_count']
            for right in rr[root].keys():
                if right == 'root_count':
                    continue

                rr[root][right] = rr[root][right] / total
                if rr[root][right] % 1 > 0:
                    f.write(root + ' -> ' + ' '.join(map(str, right)) + ' ' + str(rr[root][right]) + '\n')
                else:
                    f.write(
                        root + ' -> ' + ' '.join(map(str, right)) + ' ' + "{:d}".format(int(rr[root][right])) + '\n')
        f.close()

        f = open(name + '.lexicon', "w")
        for root in rl.keys():
            if root in rr:
                total = rr[root]['root_count'] + rl[root]['root_count']
            else:
                total = rl[root]['root_count']
            for right in rl[root].keys():
                if right == 'root_count':
                    continue

                rl[root][right] = rl[root][right] / total
                if rl[root][right] % 1 > 0:
                    f.write(root + ' ' + str(right) + ' ' + str(rl[root][right]) + '\n')
                else:
                    f.write(root + ' ' + str(right) + ' ' + "{:d}".format(int(rl[root][right])) + '\n')
            if root in rr:
                del rr[root]['root_count']
            del rl[root]['root_count']
        f.close()

        f = open(name + '.words', "w")
        for word in w:
            f.write(word + '\n')
        f.close()
