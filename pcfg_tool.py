#!/usr/bin/env python3

import sys
import induce_grammar
import parse_phrases

if len(sys.argv) < 2:
    print('ERROR: Not enough arguments.\n'
          'Syntax: pcfg_tool induce [GRAMMAR]\n'
          '        pcfg_tool parse RULES LEXICON', file=sys.stderr)
    exit(1)
if sys.argv[1] == 'induce':
    name = ''
    if len(sys.argv) > 2:
        name = sys.argv[2]
    induce_grammar.induce_grammar(name)

elif sys.argv[1] == 'parse':
    if len(sys.argv) < 4:
        print('ERROR: Not enough arguments.\n'
              'Syntax: pcfg_tool parse RULES LEXICON', file=sys.stderr)
        exit(1)
    parse_phrases.parse_phrases_cyk(sys.argv[2], sys.argv[3])

else:
    print('ERROR: ', sys.argv[1], ' is not implemented.', file=sys.stderr)
    exit(22)
