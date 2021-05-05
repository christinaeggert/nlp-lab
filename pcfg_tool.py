#!/usr/bin/env python3

import argparse
import induce_grammar

parser = argparse.ArgumentParser(description='Verarbeitung natürlicher Sprache')
parser.add_argument('func', metavar='func', type=str, nargs=1, help='one of the implemented functions (induce)')
parser.add_argument('name', metavar='name', type=str, nargs='?',
                    help='name of the grammar')

args = parser.parse_args()
if args.func[0] == 'induce':
    print('Induziere Grammatik...')
    name = ''
    if args.name:
        name = args.name
    induce_grammar.induce_grammar(name)
else:
    print('ERROR: ', args.func[0], ' is not implemented.')
    exit(22)
