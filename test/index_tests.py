
import unittest
import alveo_redis_query as alveo
import redis
import cPickle as pickle

class Test(unittest.TestCase):


    def test_tokenise(self):
        index = alveo.Index()
        
        filename = './samples/sample12.txt'
        with open(filename, 'r') as f:
            text = f.read()
            
        correct_char_offsets = [(113, 120), (121, 125), (41, 53), (104, 112),
                                (31, 40), (63, 69), (81, 96), (54, 55), (97, 103),
                                (56, 62), (20, 30), (5, 11), (12, 19), (70, 80),
                                (0, 4)]
        correct_tokens = ['10.30am', '14.9', '234.43.65.87', '3254.543',
                          '3450.3050', '345gvr', '40rjero3orejr04', 'a',
                          'a23435', 'ahfc27', 'anti-intel', "didn't", "o'clock",
                          'sfn403vtjb', 'test']
        correct_positions = [14, 15, 6, 13, 5, 9, 11, 7, 12, 8, 4, 2, 3, 10, 1]
        
        d = index._tokenise(text)
        tokens = d.keys()
        tokens.sort()
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

    def test_create_index(self):
        filename = './samples/sample10.txt'
        with open(filename, 'r') as f:
            text = f.read().lower()
        index = alveo.Index()
        tokens = index._tokenise(text)
        index._create_index_values("test", "samples", filename, tokens)

        #test that term 'information' was correctly added to the index
        redis_cli = redis.StrictRedis(host='localhost', port=6379, db="test")
        
        term = 'information'
        l = redis_cli.lrange(term, 0, -1)
        
        expected_results = ["(ialveo_redis_query.alveo_redis_query\nIndexValue\np1\n(dp2\nS'_token'\np3\nS'information'\np4\nsS'_positions'\np5\n(lp6\nI1\naI8\naI13\naI19\naI35\naI46\nasS'_item_url'\np7\nS'./samples/sample10.txt'\np8\nsS'_char_offsets'\np9\n(lp10\n(I0\nI11\ntp11\na(I51\nI62\ntp12\na(I88\nI99\ntp13\na(I126\nI137\ntp14\na(I245\nI256\ntp15\na(I316\nI327\ntp16\nasb."]
        self.assertEqual(l, expected_results, "Expected %s, got %s" %
                         (expected_results, l))

        index_value = pickle.loads(expected_results[0])


        expected_results = [(0, 11), (51, 62), (88, 99), (126, 137), (245, 256), (316, 327)]
        self.assertEqual(index_value.char_offsets, expected_results,
                         "Expected %s, got %s" % (expected_results,
                                                  index_value.char_offsets))

        expected_results = [1, 8, 13, 19, 35, 46]
        self.assertEqual(index_value.positions, expected_results,
                         "Expected %s, got %s" % (expected_results,
                                                  index_value.positions))

        #test that term 'of' was correctly added to the index
        term = 'of'
        l = redis_cli.lrange(term, 0, -1)
        
        expected_results = ["(ialveo_redis_query.alveo_redis_query\nIndexValue\np1\n(dp2\nS'_token'\np3\nS'of'\np4\nsS'_positions'\np5\n(lp6\nI6\naI18\nasS'_item_url'\np7\nS'./samples/sample10.txt'\np8\nsS'_char_offsets'\np9\n(lp10\n(I38\nI40\ntp11\na(I123\nI125\ntp12\nasb."]
        self.assertEqual(l, expected_results, "Expected %s, got %s" %
                         (expected_results, l))

        index_value = pickle.loads(expected_results[0])


        expected_results = [(38, 40), (123, 125)]
        self.assertEqual(index_value.char_offsets, expected_results,
                         "Expected %s, got %s" % (expected_results,
                                                  index_value.char_offsets))

        expected_results = [6, 18]
        self.assertEqual(index_value.positions, expected_results,
                         "Expected %s, got %s" % (expected_results,
                                                  index_value.positions))

        #test terms not present in sample10.txt are not added to the index
        term = ''
        l = redis_cli.lrange(term, 0, -1)
        expected_results = []
        self.assertEqual(l, expected_results, "Expected %s, got %s" %
                         (expected_results, l))

        term = 'pumpkin'
        l = redis_cli.lrange(term, 0, -1)
        expected_results = []
        self.assertEqual(l, expected_results, "Expected %s, got %s" %
                         (expected_results, l))

        term = 'taxi'
        l = redis_cli.lrange(term, 0, -1)
        expected_results = []
        self.assertEqual(l, expected_results, "Expected %s, got %s" %
                         (expected_results, l))
        redis_cli.flushall()
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.TextTestRunner(verbosity=2).run(unittest.makeSuite(Test))