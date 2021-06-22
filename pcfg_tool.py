#!/usr/bin/env python3

import sys
import argparse
import induce_grammar
import parse_phrases
import debinarize

if len(sys.argv) < 2:
    print('ERROR: Not enough arguments.\n'
          'Syntax: pcfg_tool induce [GRAMMAR]\n'
          '        pcfg_tool parse [OPTIONS] RULES LEXICON', file=sys.stderr)
    exit(1)
if sys.argv[1] == 'induce':
    name = ''
    if len(sys.argv) > 2:
        name = sys.argv[2]
    induce_grammar.induce_grammar(name)

elif sys.argv[1] == 'parse':
    parser = argparse.ArgumentParser(description='Verarbeitung natürlicher Sprache')
    parser.add_argument('parse', type=str, nargs=1)
    parser.add_argument('-p', '--paradigm', nargs='?', type=str, default='cyk',
                        help='parser paradigm (cyk or deductive), default: cyk')
    parser.add_argument('-i', '--initial-nonterminal', nargs='?', type=str, default='ROOT',
                        help='defines initial nonterminal, default: ROOT')
    parser.add_argument('RULES', type=str, help='file that contains the rules')
    parser.add_argument('LEXICON', type=str, help='file that contains the lexical rules')

    args = parser.parse_args()
    if args.paradigm == 'cyk':
        parse_phrases.parse_phrases_cyk(args.RULES, args.LEXICON, args.initial_nonterminal)
    elif args.paradigm == 'deductive':
        print('INFO: deductive parsing is not implemented.', file=sys.stderr)
        exit(22)
    else:
        print('ERROR:', args.paradigm, 'is not a valid argument for paradigm.', file=sys.stderr)
        exit(1)

elif sys.argv[1] == 'debinarise':
    debinarize.process_trees()

else:
    print('ERROR: ', sys.argv[1], ' is not implemented.', file=sys.stderr)
    exit(22)
