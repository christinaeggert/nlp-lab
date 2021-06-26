import sys


def debinarise(branch):
    if len(branch.split()) == 2:
        return '(' + branch + ')'

    root, branches = branch.split(' ', 1)
    # delete parents (e.g. FRAG^<ROOT> --> FRAG)
    root = root.split('^')[0]
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
        return 'err'

    ret = ''
    for new_branch in br:
        debinarised = debinarise(new_branch[1:len(new_branch) - 1])
        if debinarised == 'err':
            return debinarised
        ret += ' ' + debinarised
    ret = ret[1:len(ret)]
    if '|' not in root:
        ret = '(' + root + ' ' + ret + ')'

    return ret


def process_trees():
    for tree in sys.stdin:
        tree = tree[1:len(tree) - 2]  # cut parentheses
        print(debinarise(tree))
