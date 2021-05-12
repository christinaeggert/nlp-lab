import unittest

import induce_grammar


class TestInduceGrammar(unittest.TestCase):
    def test_lexical_rules(self):
        tree = 'nonterminal word'
        root, lexRules, rules, words = induce_grammar.get_rules(tree)
        self.assertEqual(root, 'nonterminal')
        self.assertEqual(lexRules, {'nonterminal': {'root_count': 1, 'word': 1}})
        self.assertEqual(rules, {})
        self.assertEqual(words, {'word'})

    def test_rules(self):
        tree = 'nt1 (nt2 t1)'
        root, lexRules, rules, words = induce_grammar.get_rules(tree)
        self.assertEqual(root, 'nt1')
        self.assertEqual(lexRules, {'nt2': {'root_count': 1, 't1': 1}})
        self.assertEqual(rules, {'nt1': {'root_count': 1, ('nt2',): 1}})
        self.assertEqual(words, {'t1'})

    def test_rules2(self):
        tree = 'nt1 (nt2 t1) (nt3 t2)'
        root, lexRules, rules, words = induce_grammar.get_rules(tree)
        self.assertEqual(root, 'nt1')
        self.assertEqual(lexRules, {'nt2': {'root_count': 1, 't1': 1}, 'nt3': {'root_count': 1, 't2': 1}})
        self.assertEqual(rules, {'nt1': {'root_count': 1, ('nt2', 'nt3'): 1}})
        self.assertEqual(words, {'t1', 't2'})

    def test_rules3(self):
        tree = 'nt1 (nt2 t1) (nt3 t2) (nt3 t3)'
        root, lexRules, rules, words = induce_grammar.get_rules(tree)
        self.assertEqual(root, 'nt1')
        self.assertEqual(lexRules, {'nt2': {'root_count': 1, 't1': 1}, 'nt3': {'root_count': 2, 't2': 1, 't3': 1}})
        self.assertEqual(rules, {'nt1': {'root_count': 1, ('nt2', 'nt3', 'nt3'): 1}})
        self.assertEqual(words, {'t1', 't2', 't3'})

    def test_more_opening_parentheses(self):
        tree = 'nt1 ((nt2 t1) (nt3 t2) (nt4 t3)'
        root, lexRules, rules, words = induce_grammar.get_rules(tree)
        self.assertEqual(root, 'err')
        self.assertEqual(lexRules, {})
        self.assertEqual(rules, {})
        self.assertEqual(words, [])

    def test_more_opening_parentheses2(self):
        tree = 'nt1 (nt2 ((nt5 t1) (nt3 t2) (nt4 t3))'
        root, lexRules, rules, words = induce_grammar.get_rules(tree)
        self.assertEqual(root, 'err')
        self.assertEqual(lexRules, {})
        self.assertEqual(rules, {})
        self.assertEqual(words, [])

    def test_more_closing_parentheses(self):
        tree = 'nt1 (nt2 t1) (nt3 t2) (nt4 t3'
        root, lexRules, rules, words = induce_grammar.get_rules(tree)
        self.assertEqual(root, 'err')
        self.assertEqual(lexRules, {})
        self.assertEqual(rules, {})
        self.assertEqual(words, [])

    def test_more_closing_parentheses2(self):
        tree = 'nt1 (nt2 (nt5 t1) (nt3 t2)) (nt4 t3))'
        root, lexRules, rules, words = induce_grammar.get_rules(tree)
        self.assertEqual(root, 'err')
        self.assertEqual(lexRules, {})
        self.assertEqual(rules, {})
        self.assertEqual(words, [])

    def test_illegal_tree(self):
        tree = 'nt1 (nt2 (nt5 t1) (nt3 t2) (nt4))'
        root, lexRules, rules, words = induce_grammar.get_rules(tree)
        self.assertEqual(root, 'err')
        self.assertEqual(lexRules, {})
        self.assertEqual(rules, {})
        self.assertEqual(words, [])

    def test_pre_check_spaces(self):
        tree = '   (  nt1   (  nt2  t1)(nt3 t2 ) ( nt4 t3)  )'
        self.assertEqual(induce_grammar.pre_check(tree), '(nt1 (nt2 t1) (nt3 t2) (nt4 t3))')

    def test_pre_check_parentheses(self):
        tree = '   (  nt1   (  nt2  t1)(nt3 t2 ) ( nt4 t3)'
        self.assertEqual(induce_grammar.pre_check(tree), '')


unittest.main()
