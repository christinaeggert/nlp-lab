#!/usr/bin/env python3

import argparse
import induce_grammar

parser = argparse.ArgumentParser(description='Verarbeitung natürlicher Sprache')
parser.add_argument('func', metavar='func', type=str, nargs=1, help='one of the implemented functions (induce)')
parser.add_argument('-f', default='../corpora/training.mrg',
                    help='filename of the  (default: ../corpora/training.mrg)')
parser.add_argument('-n', default='grammar1',
                    help='name of the grammar (default: grammar1)')

args = parser.parse_args()
if args.func[0] == 'induce':
    print('Induziere Grammatik...')
    induce_grammar.induce_grammar(args.f, args.n)
else:
    print('ERROR: ', args.func[0], ' is not implemented.')
    exit(22)
