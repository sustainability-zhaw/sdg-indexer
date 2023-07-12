import unittest

import re
import src.utils as utils

class Test01QuotedExpression(unittest.TestCase):
    def test_01_unquoted_expression(self):
        value = "foo"
        result = utils.parse_quoted_expression(value)
        self.assertIsNone(result)

    def test_02_quoted_expression(self):
        value = "'foo'"
        result = utils.parse_quoted_expression(value)
        self.assertEqual(result, "foo")
    
    def test_03_quoted_expression(self):
        value = "\"foo\""
        result = utils.parse_quoted_expression(value)
        self.assertEqual(result, "foo")
    
    def test_04_only_leadquote(self):
        value = "'foo"
        result = utils.parse_quoted_expression(value)
        self.assertEqual(result, "foo")

    def test_05_only_doubleleadquote(self):
        value = "\"foo"
        result = utils.parse_quoted_expression(value)
        self.assertEqual(result, "foo")
     
    def test_06_whitespace_leadin(self):
        value = " 'foo'"
        result = utils.parse_quoted_expression(value)
        self.assertEqual(result, "foo")
    
    def test_07_whitespace_doubleleadin(self):
        value = " \"foo\""
        result = utils.parse_quoted_expression(value)
        self.assertEqual(result, "foo")
    
    def test_08_whitespace_trailing(self):
        value = "'foo' "
        result = utils.parse_quoted_expression(value)
        self.assertEqual(result, "foo")
     
    def test_09_whitespace_doubletrailing(self):
        value = "\"foo\" "
        result = utils.parse_quoted_expression(value)
        self.assertEqual(result, "foo")
    
    def test_10_trail_anything(self):
        value = "'foo'bar"
        result = utils.parse_quoted_expression(value)
        self.assertEqual(result, "foo")

    def test_11_doublequote_trail_anything(self):
        value = "\"foo\"bar"
        result = utils.parse_quoted_expression(value)
        self.assertEqual(result, "foo")
    
    def test_12_strip_inner_whitespace(self):
        value = "' foo  '"
        result = utils.parse_quoted_expression(value)
        self.assertEqual(result, "\\bfoo\\b")
    
    def test_13_strip_inner_doublewhitespace(self):
        value = "\" foo  \""
        result = utils.parse_quoted_expression(value)
        self.assertEqual(result, "\\bfoo\\b")

    def test_14_normalise_inner_whitespace(self):
        value = "'foo  bar  '"
        result = utils.parse_quoted_expression(value)
        self.assertEqual(result, "foo\\ bar\\b")

    def test_15_normalise_inner_doublewhitespace(self):
        value = "\" foo  bar  baz\""
        result = utils.parse_quoted_expression(value)
        self.assertEqual(result, "\\bfoo\\ bar\\ baz")

    def test_16_multiple_quote_chars(self):
        value = "'\"foo bar\""
        result = utils.parse_quoted_expression(value)
        self.assertEqual(result, "\"foo\\ bar\"")

    def test_17_multiple_quote_chars(self):
        value = "\"'foo bar'"
        result = utils.parse_quoted_expression(value)
        self.assertEqual(result, "'foo\\ bar'")
    
    def test_18_inline_quote(self):
        value = "foo'bar"
        result = utils.parse_quoted_expression(value)
        self.assertIsNone(result)

    def test_19_multiple_quotes(self):
        value = "'foo' bar'"
        result = utils.parse_quoted_expression(value)
        self.assertEqual(result, "foo")

    def test_20_match_expression_ok(self):
        content = "this is foo bar present"
        value = "'foo bar'"
        result = utils.parse_quoted_expression(value)
        self.assertIsNotNone(result)
        self.assertEqual(result, "foo\\ bar")
        is_match = re.search(result, content, re.I) is not None
        self.assertTrue(is_match)

    
    def test_21_match_expression_not_ok(self):
        content = "this is foo present in bar"
        value = "'foo bar'"
        result = utils.parse_quoted_expression(value)
        self.assertIsNotNone(result)
        self.assertEqual(result, "foo\\ bar")
        is_match = re.search(result, content, re.I) is not None
        self.assertFalse(is_match)

    def test_22_match_expression_ok_at_end(self):
        content = "this is foo bar"
        value = "'foo bar'"
        result = utils.parse_quoted_expression(value)
        self.assertIsNotNone(result)
        self.assertEqual(result, "foo\\ bar")
        is_match = re.search(result, content, re.I) is not None
        self.assertTrue(is_match)

    def test_23_match_expression_ok_at_end_exact(self):
        content = "this is foo bar"
        value = "'foo bar "
        result = utils.parse_quoted_expression(value)
        self.assertIsNotNone(result)
        self.assertEqual(result, "foo\\ bar\\b")
        is_match = re.search(result, content, re.I) is not None
        self.assertTrue(is_match)

    def test_24_match_expression_not_ok_at_end_exact(self):
        content = "this is foo x bar"
        value = "'foo bar "
        result = utils.parse_quoted_expression(value)
        self.assertIsNotNone(result)
        self.assertEqual(result, "foo\\ bar\\b")
        is_match = re.search(result, content, re.I) is not None
        self.assertFalse(is_match)
