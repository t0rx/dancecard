#!/usr/bin/python3

import sys
import unittest
from output import *

class TestEncoding(unittest.TestCase):
  def test_format_pair(self):
    pair = [3, 1]
    self.assertEqual(format_pair(pair), 'DB')

  def test_format_session(self):
    session = [[3, 1], [0, 2], [4, 5]]
    self.assertEqual(format_session(session), 'DB AC EF')
  
  def test_format_dance(self):
    session1 = [[3, 1], [0, 2], [4, 5]]
    session2 = [[0, 4], [2, 1], [5, 3]]
    dance = [session1, session2]
    self.assertEqual(format_dance(dance), 'DB AE\nAC CB\nEF FD')

  def test_decode_pair(self):
    self.assertEqual(decode_pair('DB'), [3, 1])

  def test_decode_dance(self):
    session1 = [[3, 1], [0, 2], [4, 5]]
    session2 = [[0, 4], [2, 1], [5, 3]]
    dance = [session1, session2]    
    decoded_dance = decode_dance('DB AE\nAC CB\nEF FD')
    self.assertEqual(decoded_dance, dance)

if __name__ == '__main__':
  unittest.main()
