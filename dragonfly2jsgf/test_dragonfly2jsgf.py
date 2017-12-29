import unittest

from dragonfly import CompoundRule
from dragonfly2jsgf import *
from dragonfly import List as DragonflyList


class TranslatorCase(unittest.TestCase):
    translator = Translator()


class PlainCase(TranslatorCase):
    def test_plain(self):
        spec = "Hello world"
        expected = "public <test> = hello world;"
        rule = self.translator.translate_to_rule("test", spec, True)
        self.assertEqual(expected, rule.compile())

    def test_plain_match(self):
        spec = "Hello world"
        rule = self.translator.translate_to_rule("test", spec, True)
        self.assertTrue(rule.matches("hello world"))


class BadRuleCase(TranslatorCase):
    def test_undefined_rule(self):
        spec = "Hello <person>"
        self.assertRaises(Exception, Compound, spec)

    def test_bad_dragonfly_spec(self):
        def is_bad(spec):
            self.assertRaises(ParserError, self.translator.translate, spec)

        is_bad("Hello world[")
        is_bad("Hello world(")
        is_bad("Hello world)")
        is_bad("Hello world#")
        is_bad("Hello world<")
        is_bad("<[a]>")
        is_bad("<a>>")
        is_bad("[]")


class OptionalCase(TranslatorCase):
    def test_simple_optional(self):
        spec = "Hello [glorious] world"
        expected = "public <test> = hello [glorious] world;"
        self.assertEqual(expected,
                         self.translator.translate_to_rule("test", spec, True)
                         .compile())

    def test_complex_optional(self):
        spec = "[[hello] world] hi"
        expected = "public <test> = [[hello] world] hi;"

        self.assertEqual(expected,
                         self.translator.translate_to_rule("test", spec, True)
                         .compile())


class ListsCase(TranslatorCase):
    def setUp(self):
        self.fruit_list = DragonflyList("fruit")
        self.fruit_list.append("apple")
        self.fruit_list_ref = ListRef("fruit_ref", self.fruit_list)

    def test_list(self):
        actual = self.translator.translate_list(self.fruit_list)
        expected = jsgf.HiddenRule("fruit", jsgf.AlternativeSet("apple"))
        self.assertEqual(expected, actual)

    def test_list_ref(self):
        element = self.fruit_list_ref
        state = self.translator.translate_list_ref(TranslationState(element))
        jsgf_rule = jsgf.HiddenRule("fruit", jsgf.AlternativeSet(*self.fruit_list))
        self.assertEqual(jsgf.RuleRef(jsgf_rule), state.expansion)
        self.assertListEqual([jsgf_rule], state.dependencies)

    def test_referencing_rule(self):
        element = self.fruit_list_ref
        r = Rule("fav_fruit", element)
        state = self.translator.translate_rule(r)
        list_rule = jsgf.HiddenRule("fruit", jsgf.AlternativeSet(*self.fruit_list))
        expected_rule = LinkedRule("fav_fruit", True, jsgf.RuleRef(list_rule), r)
        self.assertEqual(state.jsgf_rule, expected_rule)


class ChoiceCase(TranslatorCase):
    """
    Test case for testing whether dragonfly choices compile correctly into
    JSGF
    """
    def test_with_choice(self):
        spec = "Hello <person>"
        compound_rule = CompoundRule(name="greet", spec=spec, extras=[
            Choice("person", {"Bob": "Bob", "John": "John"})
        ])
        expected = "public <greet> = hello (bob|john);"
        rule = self.translator.translate_rule(compound_rule).jsgf_rule
        self.assertEqual(expected, rule.compile())

    def test_choice_match(self):
        spec = "Hello <person>"
        compound_rule = CompoundRule(name="greet", spec=spec, extras=[
            Choice("person", {"Bob": "Bob", "John": "John"})
        ])
        rule = self.translator.translate_rule(compound_rule).jsgf_rule
        self.assertTrue(rule.matches("hello Bob"))


class GrammarCase(TranslatorCase):
    def test_simple_rule_grammar(self):
        grammar = Grammar("test")
        rule = CompoundRule(name="test", spec="hello world")
        grammar.add_rule(rule)
        jsgf_grammar = self.translator.translate_grammar(grammar)
        self.assertTrue(jsgf_grammar.rules[0].matches("HELLO WORLD"))


if __name__ == '__main__':
    unittest.main()