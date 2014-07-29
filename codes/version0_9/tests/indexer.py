'''
Created on 28 Jul 2014

@author: 42601487
'''
import unittest
import redis
import codes.version0_8.alveo_client as alveo
import cPickle as pickle

class IndexerTest(unittest.TestCase):

    def test_add_to_index(self):
        redis_cli = redis.StrictRedis(host='localhost', port=6379, db=0)
        redis_cli.flushall()

        filename = '../../samples/test/sample10.txt'
        text = ""
        with open(filename, 'r') as f:
            text = f.read().lower()

        alveo.Indexer._add(text, filename)

        #test that term 'information' was correctly added to the index
        term = 'information'
        l = redis_cli.lrange(term, 0, -1)
        expected_results = ["../../samples/test/sample10.txt,(icodes.version0_8.alveo_client.alveo_client\nIndexValue\np1\n(dp2\nS'_term'\np3\nS'information'\np4\nsS'_filename'\np5\nS'../../samples/test/sample10.txt'\np6\nsS'_positions'\np7\n(lp8\nI1\naI8\naI13\naI19\naI35\naI46\nasS'_char_offsets'\np9\n(lp10\n(I0\nI11\ntp11\na(I51\nI62\ntp12\na(I88\nI99\ntp13\na(I126\nI137\ntp14\na(I245\nI256\ntp15\na(I316\nI327\ntp16\nasb."]
        self.assertEqual(l, expected_results, "Expected %s, got %s" %
                         (expected_results, l))

        index_value = pickle.loads(expected_results[0].split(',')[1])


        expected_results = [(0, 11), (51, 62), (88, 99), (126, 137), (245, 256),
                            (316, 327)]
        self.assertEqual(index_value.char_offsets(), expected_results,
                         "Expected %s, got %s" % (expected_results,
                                                  index_value.char_offsets()))

        expected_results = [1, 8, 13, 19, 35, 46]
        self.assertEqual(index_value.positions(), expected_results,
                         "Expected %s, got %s" % (expected_results,
                                                  index_value.positions()))

        #test that term 'of' was correctly added to the index
        term = 'of'
        l = redis_cli.lrange(term, 0, -1)
        expected_results = ["../../samples/test/sample10.txt,(icodes.version0_8.alveo_client.alveo_client\nIndexValue\np1\n(dp2\nS'_term'\np3\nS'of'\np4\nsS'_filename'\np5\nS'../../samples/test/sample10.txt'\np6\nsS'_positions'\np7\n(lp8\nI6\naI18\nasS'_char_offsets'\np9\n(lp10\n(I38\nI40\ntp11\na(I123\nI125\ntp12\nasb."]
        self.assertEqual(l, expected_results, "Expected %s, got %s" %
                         (expected_results, l))

        index_value = pickle.loads(expected_results[0].split(',')[1])


        expected_results = [(38, 40), (123, 125)]
        self.assertEqual(index_value.char_offsets(), expected_results,
                         "Expected %s, got %s" % (expected_results,
                                                  index_value.char_offsets()))

        expected_results = [6, 18]
        self.assertEqual(index_value.positions(), expected_results,
                         "Expected %s, got %s" % (expected_results,
                                                  index_value.positions()))

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
        
    def test_update_index(self):

        redis_cli = redis.StrictRedis(host='localhost', port=6379, db=0)
        redis_cli.flushall()

        file_list = ['../../samples/test/sample9.txt', '../../samples/test/sample10.txt']

        alveo.Indexer.update(file_list)

        #test that term 'information' was correctly added to the index
        term = 'information'
        l = redis_cli.lrange(term, 0, -1)
        expected_results = ["../../samples/test/sample10.txt,(icodes.version0_8.alveo_client.alveo_client\nIndexValue\np1\n(dp2\nS'_term'\np3\nS'information'\np4\nsS'_filename'\np5\nS'../../samples/test/sample10.txt'\np6\nsS'_positions'\np7\n(lp8\nI1\naI8\naI13\naI19\naI35\naI46\nasS'_char_offsets'\np9\n(lp10\n(I0\nI11\ntp11\na(I51\nI62\ntp12\na(I88\nI99\ntp13\na(I126\nI137\ntp14\na(I245\nI256\ntp15\na(I316\nI327\ntp16\nasb."]
        self.assertEqual(l, expected_results, "Expected %s, got %s" %
                         (expected_results, l))

        index_value = pickle.loads(expected_results[0].split(',')[1])


        expected_results = [(0, 11), (51, 62), (88, 99), (126, 137), (245, 256),
                            (316, 327)]
        self.assertEqual(index_value.char_offsets(), expected_results,
                         "Expected %s, got %s" % (expected_results,
                                                  index_value.char_offsets()))

        expected_results = [1, 8, 13, 19, 35, 46]
        self.assertEqual(index_value.positions(), expected_results,
                         "Expected %s, got %s" % (expected_results,
                                                  index_value.positions()))

        #test that term 'of' was correctly added to the index
        term = 'of'
        l = redis_cli.lrange(term, 0, -1)
        expected_results = ["../../samples/test/sample10.txt,(icodes.version0_8.alveo_client.alveo_client\nIndexValue\np1\n(dp2\nS'_term'\np3\nS'of'\np4\nsS'_filename'\np5\nS'../../samples/test/sample10.txt'\np6\nsS'_positions'\np7\n(lp8\nI6\naI18\nasS'_char_offsets'\np9\n(lp10\n(I38\nI40\ntp11\na(I123\nI125\ntp12\nasb."]
        self.assertEqual(l, expected_results, "Expected %s, got %s" %
                         (expected_results, l))

        index_value = pickle.loads(expected_results[0].split(',')[1])


        expected_results = [(38, 40), (123, 125)]
        self.assertEqual(index_value.char_offsets(), expected_results,
                         "Expected %s, got %s" % (expected_results,
                                                  index_value.char_offsets()))

        expected_results = [6, 18]
        self.assertEqual(index_value.positions(), expected_results,
                         "Expected %s, got %s" % (expected_results,
                                                  index_value.positions()))

        #test that term 'beluga' was correctly added to the index
        term = 'beluga'
        l = redis_cli.lrange(term, 0, -1)
        expected_results = ["../../samples/test/sample9.txt,(icodes.version0_8.alveo_client.alveo_client\nIndexValue\np1\n(dp2\nS'_term'\np3\nS'beluga'\np4\nsS'_filename'\np5\nS'../../samples/test/sample9.txt'\np6\nsS'_positions'\np7\n(lp8\nI2\naI50\nasS'_char_offsets'\np9\n(lp10\n(I4\nI10\ntp11\na(I272\nI278\ntp12\nasb."]
        self.assertEqual(l, expected_results, "Expected %s, got %s" %
                         (expected_results, l))

        index_value = pickle.loads(expected_results[0].split(',')[1])


        expected_results = [(4, 10), (272, 278)]
        self.assertEqual(index_value.char_offsets(), expected_results,
                         "Expected %s, got %s" % (expected_results,
                                                  index_value.char_offsets()))

        expected_results = [2, 50]
        self.assertEqual(index_value.positions(), expected_results,
                         "Expected %s, got %s" % (expected_results,
                                                  index_value.positions()))

        #test that term 'predator' was correctly added to the index
        term = 'predator'
        l = redis_cli.lrange(term, 0, -1)
        expected_results = ["../../samples/test/sample9.txt,(icodes.version0_8.alveo_client.alveo_client\nIndexValue\np1\n(dp2\nS'_term'\np3\nS'predator'\np4\nsS'_filename'\np5\nS'../../samples/test/sample9.txt'\np6\nsS'_positions'\np7\n(lp8\nI6\nasS'_char_offsets'\np9\n(lp10\n(I22\nI30\ntp11\nasb."]
        self.assertEqual(l, expected_results, "Expected %s, got %s" %
                         (expected_results, l))

        index_value = pickle.loads(expected_results[0].split(',')[1])


        expected_results = [(22, 30)]
        self.assertEqual(index_value.char_offsets(), expected_results,
                         "Expected %s, got %s" % (expected_results,
                                                  index_value.char_offsets()))

        expected_results = [6]
        self.assertEqual(index_value.positions(), expected_results,
                         "Expected %s, got %s" % (expected_results,
                                                  index_value.positions()))


        #test that term 'on' was correctly added to the index
        term = 'on'
        l = redis_cli.lrange(term, 0, -1)
        expected_results = ["../../samples/test/sample9.txt,(icodes.version0_8.alveo_client.alveo_client\nIndexValue\np1\n(dp2\nS'_term'\np3\nS'on'\np4\nsS'_filename'\np5\nS'../../samples/test/sample9.txt'\np6\nsS'_positions'\np7\n(lp8\nI10\nasS'_char_offsets'\np9\n(lp10\n(I50\nI52\ntp11\nasb.",
                             "../../samples/test/sample10.txt,(icodes.version0_8.alveo_client.alveo_client\nIndexValue\np1\n(dp2\nS'_term'\np3\nS'on'\np4\nsS'_filename'\np5\nS'../../samples/test/sample10.txt'\np6\nsS'_positions'\np7\n(lp8\nI25\naI28\nasS'_char_offsets'\np9\n(lp10\n(I171\nI173\ntp11\na(I186\nI188\ntp12\nasb."]
        self.assertEqual(l, expected_results, "Expected %s, got %s" %
                         (expected_results, l))

        #test the IndexValue for sample9.txt
        index_value1 = pickle.loads(expected_results[0].split(',')[1])
        #test the IndexValue for sample10.txt
        index_value2 = pickle.loads(expected_results[1].split(',')[1])

        #test index_value1
        expected_results = [(50, 52)]
        self.assertEqual(index_value1.char_offsets(), expected_results,
                         "Expected %s, got %s" % (expected_results,
                                                  index_value1.char_offsets()))

        expected_results = [10]
        self.assertEqual(index_value1.positions(), expected_results,
                         "Expected %s, got %s" % (expected_results,
                                                  index_value2.positions()))

        #test index_value2
        expected_results = [(171, 173), (186, 188)]
        self.assertEqual(index_value2.char_offsets(), expected_results,
                         "Expected %s, got %s" % (expected_results,
                                                  index_value2.char_offsets()))

        expected_results = [25, 28]
        self.assertEqual(index_value2.positions(), expected_results,
                         "Expected %s, got %s" % (expected_results,
                                                  index_value2.positions()))

        #test terms not present in sample9.txt or sample10.txt are not added to the index
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
     


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.TextTestRunner(verbosity=2).run(unittest.makeSuite(IndexerTest))