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


def parse_phrases(rules, lexicon):
    rr = read_rulesr(rules)
    rl = read_rulesl(lexicon)

    # print(rr)
    # print(rl)

    # testsentence: the director is 61 years old .
    for phrase in sys.stdin:
        phrase = phrase[0:len(phrase) - 1].split(" ")
        
        #  use lexical rules to turn terminals into nonterminals
        c = {}
        for i in range(len(phrase)):
            c[i] = {}
            c[i][i + 1] = {}
            for lhs, rules in rl.items():
                if phrase[i] in rules:
                    c[i][i + 1][lhs] = rl[lhs][phrase[i]]

        lhs, w = max(c[0][1].items(), key=itemgetter(1))
        print(lhs + ':' + str(w))
