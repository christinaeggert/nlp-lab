import sys
from operator import itemgetter
import collections

BinaryRule = collections.namedtuple('BinaryRule', ['nonterminals', 'probability', 'child1', 'child2'])
UnaryRule = collections.namedtuple('UnaryClosure', ['nonterminal', 'probability', 'child'])
LexicalRule = collections.namedtuple('LexicalRule', ['word', 'probability'])


def read_rulesr(file):
    rr = {}
    for rule in open(file):  # rule = "A -> A1 .. An w[\n]"
        # get rid of \n if present
        if rule[len(rule) - 1] == '\n':
            rule = rule[0:len(rule) - 1]
        rule = rule.split(" ")  # get list of tokens
        lhs = rule.pop(0)  # first element is root
        w = rule.pop(len(rule) - 1)  # last element is the probability
        rhs = rule[1:len(rule)]  # cut '->' to get the right hand side of the rule
        # binarise rule
        while len(rhs) > 2:
            new_nt = rhs[len(rhs) - 2] + '_' + rhs[len(rhs) - 1]  # combine last two nonterminals to new one
            rr[new_nt] = {(rhs.pop(len(rhs) - 2), rhs.pop(len(rhs) - 1)): 1.0}  # add new rule
            rhs.append(new_nt)
        if lhs in rr:
            rr[lhs].update({tuple(rhs): float(w)})
        else:
            rr[lhs] = {tuple(rhs): float(w)}

    return rr


def read_rulesl(file):
    rl = {}
    for rule in open(file):  # rule = "A v w[\n]"
        # get rid of \n if present
        if rule[len(rule) - 1] == '\n':
            rule = rule[0:len(rule) - 1]
        lhs, rhs, w = rule.split(" ")
        if lhs in rl:
            rl[lhs].update({rhs: float(w)})
        else:
            rl[lhs] = {rhs: float(w)}

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


def construct_ptb_tree(c, root):
    if c[0][len(c)] == {} or 'ROOT' not in c[0][len(c)]:
        return False

    penn_tree = get_branch('ROOT', c, 0, len(c))
    penn_tree = penn_tree.replace('ROOT', root)
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

            for new_lhs, rules in rr.items():
                if (new_rhs,) in rules:
                    # already existing derivations can not be overridden to avoid infinite loops
                    if new_lhs not in c:
                        queue.append((new_lhs, rr[new_lhs][(new_rhs,)] * q))
                        # save used rule for back tracing
                        c[new_lhs] = UnaryRule((new_rhs,), 0, (i, j))
    return c


def parse_phrases_cyk(rules, lexicon, root):
    rr = read_rulesr(rules)
    rl = read_rulesl(lexicon)

    # testsentence: Not this year .
    for phrase in sys.stdin:
        # TODO: escape sequences?
        phrase_str = ''
        if phrase[len(phrase) - 1] == '\n':
            phrase_str = phrase[0:len(phrase) - 1]
        else:
            phrase_str = phrase
        phrase = phrase_str.split(" ")

        # initialise cost map with empty dicts
        c = dict.fromkeys(range(0, len(phrase)))
        for key in c.keys():
            c[key] = {key2: {} for key2 in range(key + 1, len(phrase) + 1)}

        #  use lexical rules to turn terminals into nonterminals
        for i in range(len(phrase)):
            for lhs, rules in rl.items():
                if phrase[i] in rules:
                    c[i][i + 1][lhs] = LexicalRule(phrase[i], rl[lhs][phrase[i]])
            c[i][i + 1] = unary_closure(rr, c[i][i + 1], i, i + 1)

        # lhs, w = max(c[0][1].items(), key=itemgetter(1))
        # print(lhs + ':' + str(w))

        # use the binary rules for the rest of the rows
        for r in range(2, len(phrase) + 1):
            for i in range(0, len(phrase) - r + 1):
                j = i + r

                for lhs, rules in rr.items():
                    for rhs in rules:
                        for m in range(i + 1, j):
                            if len(rhs) > 1:
                                child1 = c[i][m].get(rhs[0], 'none')
                                child2 = c[m][j].get(rhs[1], 'none')
                                if child1 != 'none' and child2 != 'none':
                                    prev_val = c[i][j].get(lhs, 'none')
                                    new_val = rr[lhs][rhs] * child1.probability * child2.probability
                                    if prev_val == 'none' or prev_val[1] < new_val:
                                        c[i][j][lhs] = BinaryRule(rhs, new_val, (i, m), (m, j))
                            else:
                                continue

                c[i][j] = unary_closure(rr, c[i][j], i, j)

        # TODO: variable root
        tree = construct_ptb_tree(c, root)
        if not tree:
            print('(NOPARSE ' + phrase_str + ')')
        else:
            print(tree)
