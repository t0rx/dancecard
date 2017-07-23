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


if __name__ == '__main__':
  unittest.main()
