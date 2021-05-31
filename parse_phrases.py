import sys
from operator import itemgetter


def read_rulesr(file):
    rr = {}
    for rule in open(file):  # rule = "A -> A1 .. An w\n"
        rule = rule[0:len(rule) - 1].split(" ")  # get list of tokens without \n at the end
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
    for rule in open(file):  # rule = "A v w\n"
        lhs, rhs, w = rule[0:len(rule) - 1].split(" ")
        if lhs in rl:
            rl[lhs].update({rhs: float(w)})
        else:
            rl[lhs] = {rhs: float(w)}

    return rl


def get_branch(lhs, c, i, j):
    if len(c[i][j][lhs]) == 4:
        # binary rule
        rhs, w, i_m, m_j = c[i][j][lhs]
        tree = '(' + lhs + ' ' + get_branch(rhs[0], c, i_m[0], i_m[1]) + ' ' + get_branch(rhs[1], c, m_j[0],
                                                                                          m_j[1]) + ')'
    elif len(c[i][j][lhs]) == 3:
        # unary rule
        rhs, w, i_j = c[i][j][lhs]
        tree = '(' + lhs + ' ' + get_branch(rhs[0], c, i_j[0], i_j[1]) + ')'

    elif len(c[i][j][lhs]) == 2:
        # leaf
        tree = '(' + lhs + ' ' + c[i][j][lhs][0] + ')'

    else:
        print('ERROR: illegal tuple: ', c[i][j][lhs], file=sys.stderr)
        tree = '( )'

    return tree


def construct_ptb_tree(c):
    if c[0][len(c)] == {} or 'ROOT' not in c[0][len(c)]:  # oder S nicht beinhaltet
        return 'NOPARSE'

    penn_tree = get_branch('ROOT', c, 0, len(c))
    return penn_tree


def unary_closure(rr, c):
    queue = []
    for lhs in c:
        queue.append((lhs, c[lhs][1]))
        c[lhs] = (c[lhs][0], 0, c[lhs][2], c[lhs][3])
    while len(queue) != 0:
        new_rhs, q = queue.pop(queue.index(max(queue, key=itemgetter(1))))
        if c[new_rhs][1] < q:
            c[new_rhs] = (c[new_rhs][0], q, c[new_rhs][2], c[new_rhs][3])  # rr[new_lhs][new_rhs] *
            for new_lhs, rules in rr.items():
                if (new_rhs,) in rules:
                    queue.append((new_lhs, rr[new_lhs][(new_rhs,)] * q))
                    # save used rule for back tracing
                    c[new_lhs] = ((new_rhs,), rr[new_lhs][(new_rhs,)] * q, (c[new_rhs][2][0], c[new_rhs][3][1]))
    return c


def parse_phrases_cyk(rules, lexicon):
    rr = read_rulesr(rules)
    rl = read_rulesl(lexicon)

    # testsentence: Not this year .
    for phrase in sys.stdin:
        phrase = phrase[0:len(phrase) - 1].split(" ")

        # initialise cost map with empty dicts
        c = dict.fromkeys(range(0, len(phrase)))
        for key in c.keys():
            c[key] = {key2: {} for key2 in range(key + 1, len(phrase) + 1)}

        #  use lexical rules to turn terminals into nonterminals
        for i in range(len(phrase)):
            for lhs, rules in rl.items():
                if phrase[i] in rules:
                    c[i][i + 1][lhs] = (phrase[i], rl[lhs][phrase[i]])

        # lhs, w = max(c[0][1].items(), key=itemgetter(1))
        # print(lhs + ':' + str(w))

        # use the other rules for the rest of the rows
        for r in range(2, len(phrase) + 1):
            for i in range(0, len(phrase) - r + 1):
                j = i + r

                for lhs, rules in rr.items():
                    for rhs in rules:
                        for m in range(i + 1, j):
                            if len(rhs) > 1:
                                c_im = c[i][m].get(rhs[0], 'none')
                                c_mj = c[m][j].get(rhs[1], 'none')
                                if c_im != 'none' and c_mj != 'none':
                                    prev_val = c[i][j].get(lhs, 'none')
                                    new_val = rr[lhs][rhs] * c_im[1] * c_mj[1]
                                    if prev_val == 'none' or prev_val[1] < new_val:
                                        c[i][j][lhs] = (rhs, new_val, (i, m), (m, j))
                            else:
                                continue

                c[i][j] = unary_closure(rr, c[i][j])

        print(construct_ptb_tree(c))
