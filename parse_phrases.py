import sys
from operator import itemgetter
import collections

BinaryRule = collections.namedtuple('BinaryRule', ['nonterminals', 'probability', 'child1', 'child2'])
UnaryRule = collections.namedtuple('UnaryClosure', ['nonterminal', 'probability', 'child'])
LexicalRule = collections.namedtuple('LexicalRule', ['word', 'probability'])


def read_rulesr(file):
    rr = {}  # rr[rhs0][rhs1][lhs] = w
    potential_start = set()
    nts = set()

    for rule in open(file):  # rule = "A -> A1 .. An w[\n]"
        # get rid of \n if present
        if rule[len(rule) - 1] == '\n':
            rule = rule[0:len(rule) - 1]
        rule = rule.split(" ")  # get list of tokens
        lhs = rule.pop(0)  # first element is root
        potential_start.add(lhs)
        w = rule.pop(len(rule) - 1)  # last element is the probability
        rhs = rule[1:len(rule)]  # cut '->' to get the right hand side of the rule
        nts.update(rhs)
        # binarise rule
        while len(rhs) > 2:
            new_nt = rhs[len(rhs) - 2] + '_' + rhs[len(rhs) - 1]  # combine last two nonterminals to new one
            rhs0 = rhs.pop(len(rhs) - 2)
            rhs1 = rhs.pop(len(rhs) - 2)
            if rhs0 not in rr:
                rr[rhs0] = {}
            if rhs1 not in rr[rhs0]:
                rr[rhs0][rhs1] = {}
            rr[rhs0][rhs1][new_nt] = 1.0  # add new rule
            rhs.append(new_nt)
        if rhs[0] not in rr:
            rr[rhs[0]] = {}
        if len(rhs) == 1:
            rhs.append('none')
        if rhs[1] not in rr[rhs[0]]:
            rr[rhs[0]][rhs[1]] = {}
        rr[rhs[0]][rhs[1]][lhs] = float(w)

    # find start symbol
    start = ''
    potential_start.difference_update(nts)
    if len(potential_start) == 1:
        start = potential_start.pop()
    elif len(potential_start) == 0:
        print('ERROR: no start symbol found.', file=sys.stderr)
        exit(1)
    else:
        print('ERROR: ambiguous start symbol.', file=sys.stderr)
        exit(1)

    return rr, start


def read_rulesl(file):
    rl = {}  # rl[word][lhs] = w
    for rule in open(file):  # rule = "A v w[\n]"
        # get rid of \n if present
        if rule[len(rule) - 1] == '\n':
            rule = rule[0:len(rule) - 1]
        lhs, rhs, w = rule.split(" ")
        if rhs in rl:
            rl[rhs].update({lhs: float(w)})
        else:
            rl[rhs] = {lhs: float(w)}

    return rl


def get_branch(lhs, c, i, j):
    branch = c[i][j][lhs]
    if isinstance(branch, BinaryRule):
        child1 = get_branch(branch.nonterminals[0], c, branch.child1[0], branch.child1[1])
        child2 = get_branch(branch.nonterminals[1], c, branch.child2[0], branch.child2[1])
        if child1 and child2:
            return '(' + lhs + ' ' + child1 + ' ' + child2 + ')'

    if isinstance(branch, UnaryRule):
        child = get_branch(branch.nonterminal[0], c, branch.child[0], branch.child[1])
        if child:
            return '(' + lhs + ' ' + child + ')'

    if isinstance(branch, LexicalRule):
        return '(' + lhs + ' ' + branch.word + ')'

    print('ERROR: illegal rule: ', c[i][j][lhs], file=sys.stderr)
    return False


def construct_ptb_tree(c, start, new_start):
    if c[0][len(c)] == {} or start not in c[0][len(c)]:
        return False

    penn_tree = get_branch(start, c, 0, len(c))
    penn_tree = penn_tree.replace(start, new_start)
    return penn_tree


def unary_closure(rr, c, i, j):
    queue = []
    for lhs in c:
        queue.append((lhs, c[lhs].probability))
        c[lhs] = c[lhs]._replace(probability=0)
    while len(queue) != 0:
        new_rhs, q = queue.pop(queue.index(max(queue, key=itemgetter(1))))
        if c[new_rhs].probability < q:
            c[new_rhs] = c[new_rhs]._replace(probability=q)

            if new_rhs in rr:
                if 'none' in rr[new_rhs]:
                    for new_lhs in rr[new_rhs]['none']:
                        # already existing derivations must be checked before overriding them to avoid infinite loops
                        if new_lhs in c and rr[new_rhs]['none'][new_lhs] * q < c[new_lhs].probability:
                            continue
                        queue.append((new_lhs, rr[new_rhs]['none'][new_lhs] * q))
                        # save used rule for back tracing
                        c[new_lhs] = UnaryRule((new_rhs,), 0, (i, j))

    return c


def parse_phrases_cyk(rules, lexicon, root, unking):
    rr, s = read_rulesr(rules)
    rl = read_rulesl(lexicon)

    # testsentence: Not this year .
    for phrase in sys.stdin:
        # escape sequences are my friends?
        phrase_str = ''
        if phrase[len(phrase) - 1] == '\n':
            phrase_str = phrase[0:len(phrase) - 1]
        else:
            phrase_str = phrase
        phrase = phrase_str.split(" ")
        word_map = phrase

        # initialise cost map with empty dicts
        c = dict.fromkeys(range(0, len(phrase)))
        for key in c.keys():
            c[key] = {key2: {} for key2 in range(key + 1, len(phrase) + 1)}

        #  use lexical rules to turn terminals into nonterminals
        for i in range(len(phrase)):
            if phrase[i] not in rl and unking:
                # replace unkown word with UNK
                phrase[i] = 'UNK'
            if phrase[i] in rl:
                for lhs in rl[phrase[i]]:
                    c[i][i + 1][lhs] = LexicalRule(phrase[i], rl[phrase[i]][lhs])
                c[i][i + 1] = unary_closure(rr, c[i][i + 1], i, i + 1)

        if unking:
            # restore UNK as original word
            for i in range(len(phrase)):
                for lhs in c[i][i+1]:
                    if isinstance(c[i][i+1][lhs], LexicalRule):
                        c[i][i+1][lhs]._replace(word=word_map[i])

        # lhs, w = max(c[0][1].items(), key=itemgetter(1))
        # print(lhs + ':' + str(w))

        # use the binary rules for the rest of the rows
        for r in range(2, len(phrase) + 1):
            for i in range(0, len(phrase) - r + 1):
                j = i + r

                for m in range(i + 1, j):
                    for rhs0 in c[i][m]:
                        if rhs0 in rr:
                            for rhs1 in c[m][j]:
                                if rhs1 in rr[rhs0]:
                                    for lhs in rr[rhs0][rhs1]:
                                        prev_val = c[i][j].get(lhs)
                                        new_val = rr[rhs0][rhs1][lhs] * c[i][m][rhs0].probability * c[m][j][rhs1].probability
                                        if prev_val is None or prev_val[1] < new_val:
                                            c[i][j][lhs] = BinaryRule((rhs0, rhs1), new_val, (i, m), (m, j))

                c[i][j] = unary_closure(rr, c[i][j], i, j)

        tree = construct_ptb_tree(c, s, root)
        if not tree:
            print('(NOPARSE ' + phrase_str + ')')
        else:
            print(tree)
