'''
Created on 28 Jul 2014

@author: 42601487
'''
import unittest
import redis
import codes.version0_8.alveo_client as alveo


class ProcessorTest(unittest.TestCase):

    def setUp(self):
        filelist = ['../../samples/test/sample1.txt',
                    '../../samples/test/sample2.txt',
                    '../../samples/test/sample3.txt',
                    '../../samples/test/sample8.txt',
                    '../../samples/test/sample9.txt']
        alveo.Indexer.update(filelist)


    def tearDown(self):
        redis_cli = redis.StrictRedis(host='localhost', port=6379, db=0)
        redis_cli.flushall()
        
    def check_single_term(self, term, results):
        for result in results:
            text = ""
            with open(result[0], 'r') as f:
                text = f.read().lower()
            
            for offsets in result[1]:
                found_term = text[offsets[0]:offsets[1]]
                self.assertEqual(found_term, term, "Expected %s, got %s" %
                         (term, found_term))

    def test_single_term_query(self):
        #Within these tests, also check that the start/end positions are correct
        #Note: as test/sample* files were created in windows, the newlines is '\r\n'

        #check terms that doesn't appear in the sample files
        term = 'pumpkin'
        results = alveo.QueryProcessor.single_term_query(term)
        expected_results = []
        self.assertEqual(results, expected_results, "Expected %s, got %s" %
                         (expected_results, results))
        self.check_single_term(term, results)

        term = 'taxi'
        results = alveo.QueryProcessor.single_term_query(term)
        expected_results = []
        self.assertEqual(results, expected_results, "Expected %s, got %s" %
                         (expected_results, results))
        self.check_single_term(term, results)

        term = ''
        results = alveo.QueryProcessor.single_term_query(term)
        expected_results = []
        self.assertEqual(results, expected_results, "Expected %s, got %s" %
                         (expected_results, results))
        self.check_single_term(term, results)

        #check terms that appear in the sample files
        term = 'a'
        results = alveo.QueryProcessor.single_term_query(term)
        expected_results = [('../../samples/test/sample1.txt', [(162, 163)]),
                            ('../../samples/test/sample8.txt', [(11, 12),
                                                            (161, 162)]),
                            ('../../samples/test/sample9.txt', [(14, 15),
                                                            (186, 187)])]
        self.assertEqual(results, expected_results, "Expected %s, got %s" %
                         (expected_results, results))
        self.check_single_term(term, results)

        term = 'baramulla'
        results = alveo.QueryProcessor.single_term_query(term)
        expected_results = [('../../samples/test/sample8.txt', [(49, 58)])]
        self.assertEqual(results, expected_results, "Expected %s, got %s" %
                         (expected_results, results))
        self.check_single_term(term, results)

        term = 'said'
        results = alveo.QueryProcessor.single_term_query(term)
        expected_results = [('../../samples/test/sample2.txt', [(40, 44),
                                                            (79, 83)]),
                            ('../../samples/test/sample3.txt', [(15, 19),
                                                            (68, 72)])]
        self.assertEqual(results, expected_results, "Expected %s, got %s" %
                         (expected_results, results))
        self.check_single_term(term, results)            
    
    def test_and_query(self):

        #0 valid terms
        terms = []
        results = alveo.QueryProcessor.AND_query(terms)
        expected_results = []
        self.assertEqual(results, expected_results, "Expected %s, got %s" %
                         (expected_results, results))

        #1 valid term
        terms = ['at']
        results = alveo.QueryProcessor.AND_query(terms)
        expected_results = []
        self.assertEqual(results, expected_results, "Expected %s, got %s" %
                         (expected_results, results))

        #1 valid term, 1 invalid term
        terms = ['at', 'some_string_not_in_files']
        results = alveo.QueryProcessor.AND_query(terms)
        expected_results = []
        self.assertEqual(results, expected_results, "Expected %s, got %s" %
                         (expected_results, results))

        #2 valid terms
        terms = ['said', 'the']
        results = alveo.QueryProcessor.AND_query(terms)
        expected_results = [('../../samples/test/sample2.txt', [(40, 44), (79, 83),
                                                            (45, 48), (84, 87),
                                                            (95, 98)]),
                            ('../../samples/test/sample3.txt', [(15, 19), (68, 72),
                                                            (20, 23), (73, 76)])]
        self.assertEqual(results, expected_results, "Expected %s, got %s" %
                         (expected_results, results))

        #2 valid terms, 2 invalid terms
        terms = ['said', 'some_text', 'sample2.txt', 'the']
        results = alveo.QueryProcessor.AND_query(terms)
        expected_results = []
        self.assertEqual(results, expected_results, "Expected %s, got %s" %
                         (expected_results, results))

        #3 valid terms
        terms = ['said', 'the', 'cat']
        results = alveo.QueryProcessor.AND_query(terms)
        expected_results = [('../../samples/test/sample2.txt', [(49, 52), (88, 91),
                                                            (40, 44), (79, 83),
                                                            (45, 48), (84, 87),
                                                            (95, 98)])]
        self.assertEqual(results, expected_results, "Expected %s, got %s" %
                         (expected_results, results))
        
    def test_proximity_query(self):

        term1 = "said"
        term2 = "cat"
        results = alveo.QueryProcessor.proximity_query(term1, term2)
        expected_results = []
        self.assertEqual(results, expected_results, "Expected %s, got %s" %
                         (expected_results, results))

        term1 = "said"
        term2 = "cat"
        results = alveo.QueryProcessor.proximity_query(term1, term2, 2)
        expected_results = [('../../samples/test/sample2.txt', [(40, 44), (49, 52),
                                                            (79, 83), (88, 91)])]
        self.assertEqual(results, expected_results, "Expected %s, got %s" %
                         (expected_results, results))

        term1 = "said"
        term2 = "the"
        results = alveo.QueryProcessor.proximity_query(term1, term2)
        expected_results = [('../../samples/test/sample2.txt', [(40, 44), (45, 48),
                                                            (79, 83), (84, 87)]),
                            ('../../samples/test/sample3.txt', [(15, 19), (20, 23),
                                                            (68, 72), (73, 76)])]
        self.assertEqual(results, expected_results, "Expected %s, got %s" %
                         (expected_results, results))


        #check that there is no duplicates if a term is in the proximity of
        #multiple other term.
        #e.g. "fear. Have no fear"
        term1 = "fear"
        term2 = "have"
        results = alveo.QueryProcessor.proximity_query(term1, term2, 2)
        expected_results = [('../../samples/test/sample2.txt', [(19, 23), (11, 15),
                                                            (25, 29), (33, 37)])]
        self.assertEqual(results, expected_results, "Expected %s, got %s" %
                         (expected_results, results))
    
    def test_get_proximity_offsets(self):

        result1 = ('a', [(1,2),(10,11)], [1,20])
        result2 = ('a', [(2,3),(3,4),(4,5),(5,6),(6,7),(7,8),(8,9)],
                    [2,4,6,8,10,12,16])
        results = alveo.QueryProcessor._get_proximity_offsets(result1, result2, 10)
        expected_results = [(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(10,11),(7,8),
                            (8,9)]
        self.assertEqual(results, expected_results, "Expected %s, got %s" %
                         (expected_results, results))

        result2 = ('a', [(1,2),(10,11)], [1,20])
        result1 = ('a', [(2,3),(3,4),(4,5),(5,6),(6,7),(7,8),(8,9)],
                    [2,4,6,8,10,12,16])
        results = alveo.QueryProcessor._get_proximity_offsets(result1, result2, 10)
        expected_results = [(2,3),(1,2),(3,4),(4,5),(5,6),(6,7),(10,11),(7,8),
                            (8,9)]
        self.assertEqual(results, expected_results, "Expected %s, got %s" %
                         (expected_results, results))

        result1 = ('../../samples/test/sample2.txt', [(41, 45), (82, 86)], [9, 17])
        result2 = ('../../samples/test/sample2.txt', [(50, 53), (91, 94)], [11, 19])
        results = alveo.QueryProcessor._get_proximity_offsets(result1, result2, 2)
        expected_results = [(41, 45), (50, 53), (82, 86), (91, 94)]
        self.assertEqual(results, expected_results, "Expected %s, got %s" %
                         (expected_results, results))

        result2 = ('../../samples/test/sample2.txt', [(41, 45), (82, 86)], [9, 17])
        result1 = ('../../samples/test/sample2.txt', [(50, 53), (91, 94)], [11, 19])
        results = alveo.QueryProcessor._get_proximity_offsets(result1, result2, 2)
        expected_results = [(50, 53), (41, 45), (91, 94), (82, 86)]
        self.assertEqual(results, expected_results, "Expected %s, got %s" %
                         (expected_results, results))


if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(unittest.makeSuite(ProcessorTest))