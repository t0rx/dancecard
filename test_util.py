#!/usr/bin/python3

import sys
import unittest
from util import *

class TestEncoding(unittest.TestCase):
  def test_split_host_port(self):
    host, port = split_host_port('abc:123', 456)    
    self.assertEqual(host, 'abc')
    self.assertEqual(port, 123)

  def test_split_host_port_with_default(self):
    host, port = split_host_port('def', 456)    
    self.assertEqual(host, 'def')
    self.assertEqual(port, 456)

class TestMapNamespace(unittest.TestCase):
  def test_keys_as_attrs(self):
    m = {'a': 2, 'b': 'hello'}
    n = MapNamespace(m)
    self.assertEqual(2, n.a)
    self.assertEqual('hello', n.b)

  def test_missing_name_returns_none(self):
    m = {'a': 2, 'b': 'hello'}
    n = MapNamespace(m)
    self.assertEqual(None, n.c)

  def test_iterating(self):
    m = {'a': 2, 'b': 'hello'}
    n = MapNamespace(m)
    self.assertTrue('a' in n)
    self.assertFalse('c' in n)

  def test_merge(self):
    m = {'a': 2, 'b': 'hello'}
    n = MapNamespace(m)
    self.assertFalse('c' in n)

    n.merge({'a': 4, 'c': 0})
    self.assertEqual(n.a, 4)
    self.assertEqual(n.c, 0)

  def test_merge_nones(self):
    m = {'a': 2, 'b': 'hello'}
    n = MapNamespace(m)
    self.assertFalse('c' in n)

    n.merge({'c': None})
    self.assertFalse('c' in n)

    n.merge({'c': None}, allow_nones=True)
    self.assertTrue('c' in n)

class TestMisc(unittest.TestCase):
  def test_hyphen_to_underscope(self):
    m = {'a-b': 1, 'c_d': 2}
    self.assertEqual(hyphen_to_underscore(m), {'a_b': 1, 'c_d': 2})

if __name__ == '__main__':
  unittest.main()
