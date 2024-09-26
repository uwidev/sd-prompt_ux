"""Unit testing for prompt transformation pipeline."""

import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from scripts import prompt_formatting_pipeline as pipeline


def test_get_bracket_closing():
    # Test for each opening bracket
    assert pipeline.get_bracket_closing('(') == ')'
    assert pipeline.get_bracket_closing('[') == ']'
    assert pipeline.get_bracket_closing('{') == '}'
    assert pipeline.get_bracket_closing('<') == '>'

    # # Test for invalid input (not an opening bracket)
    # with pytest.raises(ValueError):
    #     pipeline.get_bracket_closing('a')
    #
    # # Test for empty string (should raise an error)
    # with pytest.raises(ValueError):
    #     pipeline.get_bracket_closing('')
    #
    # # Test for input that's not a single character
    # with pytest.raises(TypeError):
    #     pipeline.get_bracket_closing('(())')

def test_get_bracket_opening():
    # Test for each closing bracket
    assert pipeline.get_bracket_opening(')') == '('
    assert pipeline.get_bracket_opening(']') == '['
    assert pipeline.get_bracket_opening('}') == '{'
    assert pipeline.get_bracket_opening('>') == '<'

    # # Test for invalid input (not a closing bracket)
    # with pytest.raises(ValueError):
    #     pipeline.get_bracket_opening('a')
    #
    # # Test for empty string (should raise an error)
    # with pytest.raises(ValueError):
    #     pipeline.get_bracket_opening('')
    #
    # # Test for input that's not a single character
    # with pytest.raises(TypeError):
    #     pipeline.get_bracket_opening('()')

def test_normalize_characters():
    assert pipeline.normalize_characters('ｱｲｳｴｵ') == 'アイウエオ'  # Full-width to half-width
    assert pipeline.normalize_characters('𝓣𝓮𝓼𝓽') == 'Test'  # Fraktur to regular
    assert pipeline.normalize_characters('abc') == 'abc'  # No change
    assert pipeline.normalize_characters('Hello, 世界!') == 'Hello, 世界!'  # Mixed characters

def test_tokenize():
    assert pipeline.tokenize('a,b,c') == ['a', 'b', 'c']
    assert pipeline.tokenize('1,2,3,4') == ['1', '2', '3', '4']
    assert pipeline.tokenize('apple,,banana') == ['apple', '', 'banana']
    assert pipeline.tokenize('hello') == ['hello']
    assert pipeline.tokenize('a,,b,,c') == ['a', '', 'b', '', 'c']


def test_align_brackets():
    assert pipeline.align_brackets('(   foo)') == '(foo)'
    assert pipeline.align_brackets('[   bar ]') == '[bar]'
    assert pipeline.align_brackets('{   test   }') == '{test}'
    assert pipeline.align_brackets('<   example >') == '<example>'
    assert pipeline.align_brackets('(   [   {   <   content   >   }   ]   )') == '([{<content>}])'

def test_space_and():
    assert pipeline.space_and('a   AND b') == 'a AND b'
    assert pipeline.space_and('foo ANDbar') == 'foo AND bar'
    assert pipeline.space_and('hello   AND   world') == 'hello AND world'
    assert pipeline.space_and('test ANDexample') == 'test AND example'
    assert pipeline.space_and('a AND  b AND  c') == 'a AND b AND c'
    assert pipeline.space_and('aANDbANDc') == 'a AND b AND c'

def test_align_colons():
    assert pipeline.align_colons('key: value') == 'key:value'
    assert pipeline.align_colons('foo : bar') == 'foo:bar'
    assert pipeline.align_colons('test: example') == 'test:example'
    assert pipeline.align_colons('name: John AND age: 30') == 'name:John AND age:30'
    assert pipeline.align_colons('foo bar:1.0 AND zee') == 'foo bar:1.0 AND zee'

def test_align_commas():
    assert pipeline.align_commas('a, b, c') == 'a, b, c'
    assert pipeline.align_commas('  foo ,   bar ,   baz  ') == 'foo, bar, baz'
    assert pipeline.align_commas('test,example') == 'test, example'
    assert pipeline.align_commas('  item1, item2  , item3  ') == 'item1, item2, item3'
    assert pipeline.align_commas(' , a , b , c , ') == 'a, b, c'

def test_remove_mismatched_brackets():
    assert pipeline.remove_mismatched_brackets('(a[b]c)') == '(a[b]c)'
    assert pipeline.remove_mismatched_brackets('a(b)c') == 'a(b)c'
    assert pipeline.remove_mismatched_brackets('a(b]c') == 'abc'
    assert pipeline.remove_mismatched_brackets('[(a+b)]') == '[(a+b)]'
    assert pipeline.remove_mismatched_brackets('a{b[c}d]') == 'abcd'

def test_space_bracekts():
    assert pipeline.space_bracekts(')(') == ') ('
    assert pipeline.space_bracekts('][}{') == '] [} {'
    assert pipeline.space_bracekts('foo(bar)baz') == 'foo(bar)baz'
    assert pipeline.space_bracekts('a(b)c[d]e{f}g') == 'a(b)c[d]e{f}g'
    assert pipeline.space_bracekts(')a[b]{c}') == ')a[b] {c}'

def test_align_alternating():
    assert pipeline.align_alternating('a   |b') == 'a|b'
    assert pipeline.align_alternating('foo |bar |baz') == 'foo|bar|baz'
    assert pipeline.align_alternating('test | example') == 'test|example'
    assert pipeline.align_alternating('hello | world') == 'hello|world'
    assert pipeline.align_alternating('a | b | c') == 'a|b|c'

def test_bracket_to_weights():
    assert pipeline.bracket_to_weights('(a)') == '(a:1.10)'
    assert pipeline.bracket_to_weights('((a))') == '(a:1.21)'
    assert pipeline.bracket_to_weights('((a, b))') == '(a, b:1.21)'
    assert pipeline.bracket_to_weights('(a, (b))') == '(a, (b:1.10):1.10)'
    assert pipeline.bracket_to_weights('((a), b)') == '((a:1.10), b:1.10)'
    assert pipeline.bracket_to_weights('((a), ((b)))') == '((a:1.10), (b:1.21):1.10)'

def test_space_to_underscore():
    assert pipeline.space_to_underscore('<lora:chicken butt>, multiple subjects') == '<lora:chicken butt>, multiple_subjects'
    assert pipeline.space_to_underscore('one two three') == 'one_two_three'
    assert pipeline.space_to_underscore('this is a test') == 'this_is_a_test'
    assert pipeline.space_to_underscore('<embed:foo bar>, baz') == '<embed:foo bar>, baz'
    assert pipeline.space_to_underscore('some_var_name', opposite=False) == 'some var name'

