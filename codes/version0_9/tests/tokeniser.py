'''
Created on 28 Jul 2014

@author: 42601487
'''
import unittest
import codes.version0_9.alveo_client as alveo

class TokeniserTest(unittest.TestCase):

    def test_tokeniser(self):
        
        correct_tokens = ['10.30am', '14.9', '234.43.65.87', '3254.543',
                          '3450.3050', '345gvr', '40rjero3orejr04', 'a',
                          'a23435', 'ahfc27', 'anti-intel', "didn't", "o'clock",
                          'sfn403vtjb', 'test']

        correct_char_offsets = [(113, 120), (121, 125), (41, 53), (104, 112),
                                (31, 40), (63, 69), (81, 96), (54, 55), (97, 103),
                                (56, 62), (20, 30), (5, 11), (12, 19), (70, 80),
                                (0, 4)]

        correct_positions = [14, 15, 6, 13, 5, 9, 11, 7, 12, 8, 4, 2, 3, 10, 1]
        
        filename = '../../samples/test/sample12.txt'
        text = ""
        with open(filename, 'r') as f:
            text = f.read()

        d = alveo.Tokeniser.tokenise(text)
        tokens = d.keys()
        tokens.sort()

        #check the tokens, the character offsets, and the positions

        self.assertEqual(len(tokens), len(correct_tokens),
                         "Wrong number of tokens. Expected %d, got %d" %
                         (len(correct_tokens), len(tokens)))
        
        for i in range(len(tokens)):
            self.assertEqual(tokens[i], correct_tokens[i], "Expected %s, got %s" %
                         (correct_tokens[i], tokens[i]))

            char_offset, position = d[tokens[i]][0]

            self.assertEqual(char_offset, correct_char_offsets[i], "Expected %s, got %s" %
                         (correct_char_offsets[i], char_offset))
            self.assertEqual(position, correct_positions[i], "Expected %s, got %s" %
                         (correct_positions[i], position))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.tokeniser_test']
    unittest.TextTestRunner(verbosity=2).run(unittest.makeSuite(TokeniserTest))