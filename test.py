import unittest
import pickle
from OOPgraph import Parser
from OOPgraph import Post_processing
import os
import tkinter


p = Parser(tkinter.__file__[:-11])
p.run()

pp = Post_processing('tkinter', p.list_classes, p.list_files_sizes, p.list_classes_for_html)
pp.save()

try:
    with open('test', 'rb') as f:
        origin_data = pickle.load(f)
except FileNotFoundError:
    with open('test', 'wb') as f:
        pickle.dump(pp.list_classes_for_html, f)
     
class TestStringMethods(unittest.TestCase):
    def test_equal(self):
        self.assertEqual(origin_data, pp.list_classes_for_html)

if __name__ == '__main__':
    unittest.main()
    

