import unittest
import inverted_index
import redis
import query_processor

#http://docs.python.org/2/library/unittest.html#test-cases


class HCSvLabIndexerTest(unittest.TestCase):

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

    def test_update_index(self):
        self.fail()

class HCSvLabQueryTest(unittest.TestCase):

    def setUp(self):
        filelist = ['.\\samples\\test\\sample1.txt',
                    '.\\samples\\test\\sample2.txt',
                    '.\\samples\\test\\sample3.txt',
                    '.\\samples\\test\\sample8.txt',
                    '.\\samples\\test\\sample9.txt']
        inverted_index.update_index(filelist)


    def tearDown(self):
        r = redis.StrictRedis(host='localhost', port=6379, db=0)
        r.flushall()

    def test_single_term_query(self):
        #Within these tests, also check that the start/end positions are correct
        #Note: as files were created in windows, the newlines as '\r\n'
        
        self.fail()

    def test_and_query(self):

        #0 valid terms
        terms = []
        results = query_processor.and_query(terms)
        expected_results = []
        self.assertEqual(results, expected_results, "Expected %s, got %s" %
                         (expected_results, results))

        #1 valid term
        terms = ['at']
        results = query_processor.and_query(terms)
        expected_results = []
        self.assertEqual(results, expected_results, "Expected %s, got %s" %
                         (expected_results, results))

        #1 valid term, 1 invalid term
        terms = ['at', 'some_string_not_in_files']
        results = query_processor.and_query(terms)
        expected_results = []
        self.assertEqual(results, expected_results, "Expected %s, got %s" %
                         (expected_results, results))

        #2 valid terms
        terms = ['said', 'the']
        results = query_processor.and_query(terms)
        expected_results = [('.\\samples\\test\\sample2.txt', ([(41, 45),
                                                                (82, 86)],
                                                               [(46, 49),
                                                                (87, 90),
                                                                (98, 101)])),
                            ('.\\samples\\test\\sample3.txt', ([(15, 19),
                                                                (70, 74)],
                                                               [(20, 23),
                                                                (75, 78)]))]
        self.assertEqual(results, expected_results, "Expected %s, got %s" %
                         (expected_results, results))

        #2 valid terms, 2 invalid terms
        terms = ['said', 'some_text', 'sample2.txt', 'the']
        results = query_processor.and_query(terms)
        expected_results = []
        self.assertEqual(results, expected_results, "Expected %s, got %s" %
                         (expected_results, results))

        #3 valid terms
        terms = ['said', 'the', 'cat']
        results = query_processor.and_query(terms)
        expected_results = [('.\\samples\\test\\sample2.txt', (([(50, 53),
                                                                 (91, 94)],
                                                                [(41, 45),
                                                                 (82, 86)]),
                                                               [(46, 49),
                                                                (87, 90),
                                                                (98, 101)]))]
        self.assertEqual(results, expected_results, "Expected %s, got %s" %
                         (expected_results, results))

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(unittest.makeSuite(HCSvLabIndexerTest))
    unittest.TextTestRunner(verbosity=2).run(unittest.makeSuite(HCSvLabQueryTest))
