import sys
sys.path.append("..")

import unittest

import re

import app.utils_spacy as utils

class Test01QuotedExpression(unittest.TestCase):
    def test_01_unquoted_expression(self):
        value = "foo"
        result = utils.parse_quoted_expression(value)
        self.assertEqual(result["value"], "foo")
        self.assertFalse(result["quote"])

    def test_02_quoted_expression(self):
        value = "'foo'"
        result = utils.parse_quoted_expression(value)
        self.assertEqual(result["value"], "foo")
        self.assertTrue(result["quote"])
        self.assertFalse(result["match_start"])
        self.assertFalse(result["match_end"])
    
    def test_03_quoted_expression(self):
        value = "\"foo\""
        result = utils.parse_quoted_expression(value)
        self.assertEqual(result["value"], "foo")
        self.assertTrue(result["quote"])
        self.assertFalse(result["match_start"])
        self.assertFalse(result["match_end"])
    
    def test_04_only_leadquote(self):
        value = "'foo"
        result = utils.parse_quoted_expression(value)
        self.assertEqual(result["value"], "foo")
        self.assertTrue(result["quote"])
        self.assertFalse(result["match_start"])
        self.assertFalse(result["match_end"])

    def test_05_only_doubleleadquote(self):
        value = "\"foo"
        result = utils.parse_quoted_expression(value)
        self.assertEqual(result["value"], "foo")
        self.assertTrue(result["quote"])
        self.assertFalse(result["match_start"])
        self.assertFalse(result["match_end"])
     
    def test_06_whitespace_leadin(self):
        value = " 'foo'"
        result = utils.parse_quoted_expression(value)
        self.assertEqual(result["value"], "foo")
        self.assertTrue(result["quote"])
        self.assertFalse(result["match_start"])
        self.assertFalse(result["match_end"])
    
    def test_07_whitespace_doubleleadin(self):
        value = " \"foo\""
        result = utils.parse_quoted_expression(value)
        self.assertEqual(result["value"], "foo")
        self.assertTrue(result["quote"])
        self.assertFalse(result["match_start"])
        self.assertFalse(result["match_end"])
    
    def test_08_whitespace_trailing(self):
        value = "'foo' "
        result = utils.parse_quoted_expression(value)
        self.assertEqual(result["value"], "foo")
        self.assertTrue(result["quote"])
        self.assertFalse(result["match_start"])
        self.assertFalse(result["match_end"])
     
    def test_09_whitespace_doubletrailing(self):
        value = "\"foo\" "
        result = utils.parse_quoted_expression(value)
        
        self.assertEqual(result["value"], "foo")
        self.assertTrue(result["quote"])
        self.assertFalse(result["match_start"])
        self.assertFalse(result["match_end"])
    
    def test_10_trail_anything(self):
        value = "'foo'bar"
        result = utils.parse_quoted_expression(value)
        
        self.assertEqual(result["value"], "foo")
        self.assertTrue(result["quote"])
        self.assertFalse(result["match_start"])
        self.assertFalse(result["match_end"])

    def test_11_doublequote_trail_anything(self):
        value = "\"foo\"bar"
        result = utils.parse_quoted_expression(value)
        
        self.assertEqual(result["value"], "foo")
        self.assertTrue(result["quote"])
        self.assertFalse(result["match_start"])
        self.assertFalse(result["match_end"])
    
    def test_12_strip_inner_whitespace(self):
        value = "' foo  '"
        result = utils.parse_quoted_expression(value)
        
        self.assertEqual(result["value"], "foo")
        self.assertTrue(result["quote"])
        self.assertTrue(result["match_start"])
        self.assertTrue(result["match_end"])
    
    def test_13_strip_inner_doublewhitespace(self):
        value = "\" foo  \""
        result = utils.parse_quoted_expression(value)
      
        self.assertEqual(result["value"], "foo")
        self.assertTrue(result["quote"])
        self.assertTrue(result["match_start"])
        self.assertTrue(result["match_end"])

    def test_14_normalise_inner_whitespace(self):
        value = "'foo  bar  '"
        result = utils.parse_quoted_expression(value)
        self.assertEqual(result["value"], "foo bar")
        self.assertTrue(result["quote"])
        self.assertFalse(result["match_start"])
        self.assertTrue(result["match_end"])

    def test_15_normalise_inner_doublewhitespace(self):
        value = "\" foo  bar  baz\""
        result = utils.parse_quoted_expression(value)
        self.assertEqual(result["value"], "foo bar baz" )
        self.assertTrue(result["quote"])
        self.assertTrue(result["match_start"])
        self.assertFalse(result["match_end"])

    def test_16_multiple_quote_chars(self):
        value = "'\"foo bar\""
        result = utils.parse_quoted_expression(value)
        self.assertEqual(result["value"], "\"foo bar\"")
        self.assertTrue(result["quote"])
        self.assertFalse(result["match_start"])
        self.assertFalse(result["match_end"])

    def test_17_multiple_quote_chars(self):
        value = "\"'foo bar'"
        result = utils.parse_quoted_expression(value)
        self.assertEqual(result["value"], "'foo bar'")
        self.assertTrue(result["quote"])
        self.assertFalse(result["match_start"])
        self.assertFalse(result["match_end"])
    
    def test_18_inline_quote(self):
        value = "foo'bar"
        result = utils.parse_quoted_expression(value)
        self.assertEqual(result["value"], "foo'bar")
        self.assertFalse(result["quote"])
        

    def test_19_multiple_quotes(self):
        value = "'foo' bar'"
        result = utils.parse_quoted_expression(value)
        self.assertEqual(result["value"], "foo")
        self.assertTrue(result["quote"])
        self.assertFalse(result["match_start"])
        self.assertFalse(result["match_end"])

    
    def test_20_quoted_expression_1(self):
        quoted_expression = utils.parse_quoted_expression('shanty towns "')
        self.assertFalse(quoted_expression["quote"])

    def test_21_quoted_expression_2(self):
        quoted_expression = utils.parse_quoted_expression('" shanty towns "')
        self.assertEqual(quoted_expression["value"], "shanty towns")
        self.assertTrue(quoted_expression["match_start"])
        self.assertTrue(quoted_expression["match_end"])

    def test_22_quoted_expression_3(self):
        quoted_expression = utils.parse_quoted_expression('"shanty towns "')
        self.assertEqual(quoted_expression["value"], "shanty towns")
        self.assertFalse(quoted_expression["match_start"])
        self.assertTrue(quoted_expression["match_end"])


    def test_23_quoted_expression_4(self):
        quoted_expression = utils.parse_quoted_expression('" shanty towns"')
        self.assertEqual(quoted_expression["value"], "shanty towns")
        self.assertTrue(quoted_expression["match_start"])
        self.assertFalse(quoted_expression["match_end"])

    def test_24_quoted_expression_5(self):
        quoted_expression = utils.parse_quoted_expression('" shanty towns')
        self.assertEqual(quoted_expression["value"], "shanty towns")
        self.assertTrue(quoted_expression["match_start"])
        self.assertFalse(quoted_expression["match_end"])

    def test_25_quoted_expression_6(self):
        quoted_expression = utils.parse_quoted_expression('" shanty towns  ')
        self.assertEqual(quoted_expression["value"], "shanty towns")
        self.assertTrue(quoted_expression["match_start"])
        self.assertTrue(quoted_expression["match_end"])

    def test_26_quoted_expression_7(self):
        quoted_expression = utils.parse_quoted_expression('" shanty  towns  ')
        self.assertEqual(quoted_expression["value"], "shanty towns")
        self.assertTrue(quoted_expression["match_start"])
        self.assertTrue(quoted_expression["match_end"])
