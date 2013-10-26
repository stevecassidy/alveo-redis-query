import unittest
import inverted_index

#http://docs.python.org/2/library/unittest.html#test-cases


class HCSvLabTest(unittest.TestCase):

    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    def test_tokenizer(self):

        correct_tokens = ['10.30am', '14.9', '234.43.65.87', '3254.543',
                          '3450.3050', '345gvr', '40rjero3orejr04', 'a',
                          'a23435', 'ahfc27', 'anti-intel', "didn't", "o'clock",
                          'sfn403vtjb', 'test']
        

        filename = '.\\samples\\test\\sample12.txt'
        #get the text file
        f = open(filename, 'r')
        text = f.read()
        f.close()

        #tokenize the text
        tokens = inverted_index.tokenize(text).keys()
        tokens.sort()

        #check the tokens

        self.assertEqual(len(tokens), len(correct_tokens),
                         "Wrong number of tokens. Expected %d, got %d" %
                         (len(correct_tokens), len(tokens)))
        
        for i in range(len(tokens)):
            self.assertEqual(tokens[i], correct_tokens[i], "Expected %s, got %s" %
                         (correct_tokens[i], tokens[i]))

    def test_add_to_index(self):
        self.fail()

    def test_create_index(self):
        self.fail()

    def test_single_term_query(self):
        self.fail()


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(unittest.makeSuite(HCSvLabTest))
