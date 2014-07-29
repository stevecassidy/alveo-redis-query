import unittest
import inverted_index
import redis
import query_processor
import cPickle as pickle

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

        correct_char_offsets = [(125, 132), (134, 138), (46, 58), (115, 123),
                                (35, 44), (71, 77), (91, 106), (60, 61), (108, 114),
                                (63, 69), (23, 33), (6, 12), (14, 21), (79, 89),
                                (0, 4)]

        correct_positions = [14, 15, 6, 13, 5, 9, 11, 7, 12, 8, 4, 2, 3, 10, 1]
        
        filename = './samples/test/sample12.txt'
        #get the text file
        text = ""
        with open(filename, 'r') as f:
            text = f.read()

        #tokenize the text
        d = inverted_index.tokenize(text)
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
            

    def test_add_to_index(self):
        r = redis.StrictRedis(host='localhost', port=6379, db=0)
        r.flushall()

        filename = './samples/test/sample10.txt'
        text = ""
        with open(filename, 'r') as f:
            text = f.read().lower()

        inverted_index.add_to_index(text, filename)

        #test that term 'information' was correctly added to the index
        term = 'information'
        l = r.lrange(term, 0, -1)
        expected_results = ["./samples/test/sample10.txt,(iindex_value\nIndexValue\np1\n(dp2\nS'_term'\np3\nS'information'\np4\nsS'_filename'\np5\nS'./samples/test/sample10.txt'\np6\nsS'_positions'\np7\n(lp8\nI1\naI8\naI13\naI19\naI35\naI46\nasS'_char_offsets'\np9\n(lp10\n(I0\nI11\ntp11\na(I51\nI62\ntp12\na(I88\nI99\ntp13\na(I126\nI137\ntp14\na(I247\nI258\ntp15\na(I318\nI329\ntp16\nasb."]
        self.assertEqual(l, expected_results, "Expected %s, got %s" %
                         (expected_results, l))

        index_value = pickle.loads(expected_results[0].split(',')[1])


        expected_results = [(0, 11), (51, 62), (88, 99), (126, 137), (247, 258),
                            (318, 329)]
        self.assertEqual(index_value.get_char_offsets(), expected_results,
                         "Expected %s, got %s" % (expected_results,
                                                  index_value.get_char_offsets()))

        expected_results = [1, 8, 13, 19, 35, 46]
        self.assertEqual(index_value.get_positions(), expected_results,
                         "Expected %s, got %s" % (expected_results,
                                                  index_value.get_positions()))

        #test that term 'of' was correctly added to the index
        term = 'of'
        l = r.lrange(term, 0, -1)
        expected_results = ["./samples/test/sample10.txt,(iindex_value\nIndexValue\np1\n(dp2\nS'_term'\np3\nS'of'\np4\nsS'_filename'\np5\nS'./samples/test/sample10.txt'\np6\nsS'_positions'\np7\n(lp8\nI6\naI18\nasS'_char_offsets'\np9\n(lp10\n(I38\nI40\ntp11\na(I123\nI125\ntp12\nasb."]
        self.assertEqual(l, expected_results, "Expected %s, got %s" %
                         (expected_results, l))

        index_value = pickle.loads(expected_results[0].split(',')[1])


        expected_results = [(38, 40), (123, 125)]
        self.assertEqual(index_value.get_char_offsets(), expected_results,
                         "Expected %s, got %s" % (expected_results,
                                                  index_value.get_char_offsets()))

        expected_results = [6, 18]
        self.assertEqual(index_value.get_positions(), expected_results,
                         "Expected %s, got %s" % (expected_results,
                                                  index_value.get_positions()))

        #test terms not present in sample10.txt are not added to the index
        term = ''
        l = r.lrange(term, 0, -1)
        expected_results = []
        self.assertEqual(l, expected_results, "Expected %s, got %s" %
                         (expected_results, l))

        term = 'pumpkin'
        l = r.lrange(term, 0, -1)
        expected_results = []
        self.assertEqual(l, expected_results, "Expected %s, got %s" %
                         (expected_results, l))

        term = 'taxi'
        l = r.lrange(term, 0, -1)
        expected_results = []
        self.assertEqual(l, expected_results, "Expected %s, got %s" %
                         (expected_results, l))
        

    def test_update_index(self):

        r = redis.StrictRedis(host='localhost', port=6379, db=0)
        r.flushall()

        file_list = ['./samples/test/sample9.txt', './samples/test/sample10.txt']

        inverted_index.update_index(file_list)

        #test that term 'information' was correctly added to the index
        term = 'information'
        l = r.lrange(term, 0, -1)
        expected_results = ["./samples/test/sample10.txt,(iindex_value\nIndexValue\np1\n(dp2\nS'_term'\np3\nS'information'\np4\nsS'_filename'\np5\nS'./samples/test/sample10.txt'\np6\nsS'_positions'\np7\n(lp8\nI1\naI8\naI13\naI19\naI35\naI46\nasS'_char_offsets'\np9\n(lp10\n(I0\nI11\ntp11\na(I51\nI62\ntp12\na(I88\nI99\ntp13\na(I126\nI137\ntp14\na(I247\nI258\ntp15\na(I318\nI329\ntp16\nasb."]
        self.assertEqual(l, expected_results, "Expected %s, got %s" %
                         (expected_results, l))

        index_value = pickle.loads(expected_results[0].split(',')[1])


        expected_results = [(0, 11), (51, 62), (88, 99), (126, 137), (247, 258),
                            (318, 329)]
        self.assertEqual(index_value.get_char_offsets(), expected_results,
                         "Expected %s, got %s" % (expected_results,
                                                  index_value.get_char_offsets()))

        expected_results = [1, 8, 13, 19, 35, 46]
        self.assertEqual(index_value.get_positions(), expected_results,
                         "Expected %s, got %s" % (expected_results,
                                                  index_value.get_positions()))

        #test that term 'of' was correctly added to the index
        term = 'of'
        l = r.lrange(term, 0, -1)
        expected_results = ["./samples/test/sample10.txt,(iindex_value\nIndexValue\np1\n(dp2\nS'_term'\np3\nS'of'\np4\nsS'_filename'\np5\nS'./samples/test/sample10.txt'\np6\nsS'_positions'\np7\n(lp8\nI6\naI18\nasS'_char_offsets'\np9\n(lp10\n(I38\nI40\ntp11\na(I123\nI125\ntp12\nasb."]
        self.assertEqual(l, expected_results, "Expected %s, got %s" %
                         (expected_results, l))

        index_value = pickle.loads(expected_results[0].split(',')[1])


        expected_results = [(38, 40), (123, 125)]
        self.assertEqual(index_value.get_char_offsets(), expected_results,
                         "Expected %s, got %s" % (expected_results,
                                                  index_value.get_char_offsets()))

        expected_results = [6, 18]
        self.assertEqual(index_value.get_positions(), expected_results,
                         "Expected %s, got %s" % (expected_results,
                                                  index_value.get_positions()))

        #test that term 'beluga' was correctly added to the index
        term = 'beluga'
        l = r.lrange(term, 0, -1)
        expected_results = ["./samples/test/sample9.txt,(iindex_value\nIndexValue\np1\n(dp2\nS'_term'\np3\nS'beluga'\np4\nsS'_filename'\np5\nS'./samples/test/sample9.txt'\np6\nsS'_positions'\np7\n(lp8\nI2\naI50\nasS'_char_offsets'\np9\n(lp10\n(I4\nI10\ntp11\na(I274\nI280\ntp12\nasb."]
        self.assertEqual(l, expected_results, "Expected %s, got %s" %
                         (expected_results, l))

        index_value = pickle.loads(expected_results[0].split(',')[1])


        expected_results = [(4, 10), (274, 280)]
        self.assertEqual(index_value.get_char_offsets(), expected_results,
                         "Expected %s, got %s" % (expected_results,
                                                  index_value.get_char_offsets()))

        expected_results = [2, 50]
        self.assertEqual(index_value.get_positions(), expected_results,
                         "Expected %s, got %s" % (expected_results,
                                                  index_value.get_positions()))

        #test that term 'predator' was correctly added to the index
        term = 'predator'
        l = r.lrange(term, 0, -1)
        expected_results = ["./samples/test/sample9.txt,(iindex_value\nIndexValue\np1\n(dp2\nS'_term'\np3\nS'predator'\np4\nsS'_filename'\np5\nS'./samples/test/sample9.txt'\np6\nsS'_positions'\np7\n(lp8\nI6\nasS'_char_offsets'\np9\n(lp10\n(I22\nI30\ntp11\nasb."]
        self.assertEqual(l, expected_results, "Expected %s, got %s" %
                         (expected_results, l))

        index_value = pickle.loads(expected_results[0].split(',')[1])


        expected_results = [(22, 30)]
        self.assertEqual(index_value.get_char_offsets(), expected_results,
                         "Expected %s, got %s" % (expected_results,
                                                  index_value.get_char_offsets()))

        expected_results = [6]
        self.assertEqual(index_value.get_positions(), expected_results,
                         "Expected %s, got %s" % (expected_results,
                                                  index_value.get_positions()))


        #test that term 'on' was correctly added to the index
        term = 'on'
        l = r.lrange(term, 0, -1)
        expected_results = ["./samples/test/sample9.txt,(iindex_value\nIndexValue\np1\n(dp2\nS'_term'\np3\nS'on'\np4\nsS'_filename'\np5\nS'./samples/test/sample9.txt'\np6\nsS'_positions'\np7\n(lp8\nI10\nasS'_char_offsets'\np9\n(lp10\n(I50\nI52\ntp11\nasb.",
                            "./samples/test/sample10.txt,(iindex_value\nIndexValue\np1\n(dp2\nS'_term'\np3\nS'on'\np4\nsS'_filename'\np5\nS'./samples/test/sample10.txt'\np6\nsS'_positions'\np7\n(lp8\nI25\naI28\nasS'_char_offsets'\np9\n(lp10\n(I171\nI173\ntp11\na(I186\nI188\ntp12\nasb."]
        self.assertEqual(l, expected_results, "Expected %s, got %s" %
                         (expected_results, l))

        #test the IndexValue for sample9.txt
        index_value1 = pickle.loads(expected_results[0].split(',')[1])
        #test the IndexValue for sample10.txt
        index_value2 = pickle.loads(expected_results[1].split(',')[1])

        #test index_value1
        expected_results = [(50, 52)]
        self.assertEqual(index_value1.get_char_offsets(), expected_results,
                         "Expected %s, got %s" % (expected_results,
                                                  index_value1.get_char_offsets()))

        expected_results = [10]
        self.assertEqual(index_value1.get_positions(), expected_results,
                         "Expected %s, got %s" % (expected_results,
                                                  index_value2.get_positions()))

        #test index_value2
        expected_results = [(171, 173), (186, 188)]
        self.assertEqual(index_value2.get_char_offsets(), expected_results,
                         "Expected %s, got %s" % (expected_results,
                                                  index_value2.get_char_offsets()))

        expected_results = [25, 28]
        self.assertEqual(index_value2.get_positions(), expected_results,
                         "Expected %s, got %s" % (expected_results,
                                                  index_value2.get_positions()))

        #test terms not present in sample9.txt or sample10.txt are not added to the index
        term = ''
        l = r.lrange(term, 0, -1)
        expected_results = []
        self.assertEqual(l, expected_results, "Expected %s, got %s" %
                         (expected_results, l))

        term = 'pumpkin'
        l = r.lrange(term, 0, -1)
        expected_results = []
        self.assertEqual(l, expected_results, "Expected %s, got %s" %
                         (expected_results, l))

        term = 'taxi'
        
        l = r.lrange(term, 0, -1)
        expected_results = []
        self.assertEqual(l, expected_results, "Expected %s, got %s" %
                         (expected_results, l))
        
        

class HCSvLabQueryTest(unittest.TestCase):

    def setUp(self):
        filelist = ['./samples/test/sample1.txt',
                    './samples/test/sample2.txt',
                    './samples/test/sample3.txt',
                    './samples/test/sample8.txt',
                    './samples/test/sample9.txt']
        inverted_index.update_index(filelist)


    def tearDown(self):
        r = redis.StrictRedis(host='localhost', port=6379, db=0)
        r.flushall()

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
        results = query_processor.single_term_query(term)
        expected_results = []
        self.assertEqual(results, expected_results, "Expected %s, got %s" %
                         (expected_results, results))
        self.check_single_term(term, results)

        term = 'taxi'
        results = query_processor.single_term_query(term)
        expected_results = []
        self.assertEqual(results, expected_results, "Expected %s, got %s" %
                         (expected_results, results))
        self.check_single_term(term, results)

        term = ''
        results = query_processor.single_term_query(term)
        expected_results = []
        self.assertEqual(results, expected_results, "Expected %s, got %s" %
                         (expected_results, results))
        self.check_single_term(term, results)

        #check terms that appear in the sample files
        term = 'a'
        results = query_processor.single_term_query(term)
        expected_results = [('./samples/test/sample1.txt', [(164, 165)]),
                            ('./samples/test/sample8.txt', [(11, 12),
                                                            (161, 162)]),
                            ('./samples/test/sample9.txt', [(14, 15),
                                                            (186, 187)])]
        self.assertEqual(results, expected_results, "Expected %s, got %s" %
                         (expected_results, results))
        self.check_single_term(term, results)

        term = 'baramulla'
        results = query_processor.single_term_query(term)
        expected_results = [('./samples/test/sample8.txt', [(49, 58)])]
        self.assertEqual(results, expected_results, "Expected %s, got %s" %
                         (expected_results, results))
        self.check_single_term(term, results)

        term = 'said'
        results = query_processor.single_term_query(term)
        expected_results = [('./samples/test/sample2.txt', [(41, 45),
                                                            (82, 86)]),
                            ('./samples/test/sample3.txt', [(15, 19),
                                                            (70, 74)])]
        self.assertEqual(results, expected_results, "Expected %s, got %s" %
                         (expected_results, results))
        self.check_single_term(term, results)
        
        

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
        expected_results = [('./samples/test/sample2.txt', [(41, 45), (82, 86),
                                                            (46, 49), (87, 90),
                                                            (98, 101)]),
                            ('./samples/test/sample3.txt', [(15, 19), (70, 74),
                                                            (20, 23), (75, 78)])]
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
        expected_results = [('./samples/test/sample2.txt', [(50, 53), (91, 94),
                                                            (41, 45), (82, 86),
                                                            (46, 49), (87, 90),
                                                            (98, 101)])]
        self.assertEqual(results, expected_results, "Expected %s, got %s" %
                         (expected_results, results))

    def test_proximity_query(self):

        term1 = "said"
        term2 = "cat"
        results = query_processor.proximity_query(term1, term2)
        expected_results = []
        self.assertEqual(results, expected_results, "Expected %s, got %s" %
                         (expected_results, results))

        term1 = "said"
        term2 = "cat"
        results = query_processor.proximity_query(term1, term2, 2)
        expected_results = [('./samples/test/sample2.txt', [(41, 45), (50, 53),
                                                            (82, 86), (91, 94)])]
        self.assertEqual(results, expected_results, "Expected %s, got %s" %
                         (expected_results, results))

        term1 = "said"
        term2 = "the"
        results = query_processor.proximity_query(term1, term2)
        expected_results = [('./samples/test/sample2.txt', [(41, 45), (46, 49),
                                                            (82, 86), (87, 90)]),
                            ('./samples/test/sample3.txt', [(15, 19), (20, 23),
                                                            (70, 74), (75, 78)])]
        self.assertEqual(results, expected_results, "Expected %s, got %s" %
                         (expected_results, results))


        #check that there is no duplicates if a term is in the proximity of
        #multiple other term.
        #e.g. "fear. Have no fear"
        term1 = "fear"
        term2 = "have"
        results = query_processor.proximity_query(term1, term2, 2)
        expected_results = [('./samples/test/sample2.txt', [(19, 23), (11, 15),
                                                            (26, 30), (34, 38)])]
        self.assertEqual(results, expected_results, "Expected %s, got %s" %
                         (expected_results, results))
        
    def test__get_proximity_results(self):

        result1 = ('a', [(1,2),(10,11)], [1,20])
        result2 = ('a', [(2,3),(3,4),(4,5),(5,6),(6,7),(7,8),(8,9)],
                    [2,4,6,8,10,12,16])
        results = query_processor._get_proximity_results(result1, result2, 10)
        expected_results = [(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(10,11),(7,8),
                            (8,9)]
        self.assertEqual(results, expected_results, "Expected %s, got %s" %
                         (expected_results, results))

        result2 = ('a', [(1,2),(10,11)], [1,20])
        result1 = ('a', [(2,3),(3,4),(4,5),(5,6),(6,7),(7,8),(8,9)],
                    [2,4,6,8,10,12,16])
        results = query_processor._get_proximity_results(result1, result2, 10)
        expected_results = [(2,3),(1,2),(3,4),(4,5),(5,6),(6,7),(10,11),(7,8),
                            (8,9)]
        self.assertEqual(results, expected_results, "Expected %s, got %s" %
                         (expected_results, results))

        result1 = ('./samples/test/sample2.txt', [(41, 45), (82, 86)], [9, 17])
        result2 = ('./samples/test/sample2.txt', [(50, 53), (91, 94)], [11, 19])
        results = query_processor._get_proximity_results(result1, result2, 2)
        expected_results = [(41, 45), (50, 53), (82, 86), (91, 94)]
        self.assertEqual(results, expected_results, "Expected %s, got %s" %
                         (expected_results, results))

        result2 = ('./samples/test/sample2.txt', [(41, 45), (82, 86)], [9, 17])
        result1 = ('./samples/test/sample2.txt', [(50, 53), (91, 94)], [11, 19])
        results = query_processor._get_proximity_results(result1, result2, 2)
        expected_results = [(50, 53), (41, 45), (91, 94), (82, 86)]
        self.assertEqual(results, expected_results, "Expected %s, got %s" %
                         (expected_results, results))


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(unittest.makeSuite(HCSvLabIndexerTest))
    unittest.TextTestRunner(verbosity=2).run(unittest.makeSuite(HCSvLabQueryTest))
