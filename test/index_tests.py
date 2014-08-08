
import unittest
import alveo_redis_query as alveo
import redis
import cPickle as pickle

class Test(unittest.TestCase):

    documents = ['test/samples/sample1.txt',
                'test/samples/sample2.txt',
                'test/samples/sample3.txt',
                'test/samples/sample4.txt',
                'test/samples/sample5.txt',
                'test/samples/sample6.txt',
                'test/samples/sample7.txt',
                'test/samples/sample8.txt',
                'test/samples/sample9.txt',
                'test/samples/sample10.txt',
                'test/samples/sample11.txt',
                'test/samples/sample12.txt',
                ]

    def test_tokenise(self):
        index = alveo.Index()
        
        filename = 'test/samples/sample12.txt'
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

    def test_index_documents(self):

        index = alveo.Index()
        index.clear()

        for filename in self.documents:
            index.index_document(filename)

        #test that term 'information' was correctly added to the index
        redis_cli = index.redis
        
        term = 'this'
        
        hits = index.get_entry(term)
        
        self.assertEqual(3, len(hits), "Expected three documents to match query for 'this'")
        
        hitdocs = [hit.docid for hit in hits]
        self.assertIn('test/samples/sample3.txt', hitdocs)
        self.assertIn('test/samples/sample6.txt', hitdocs)
        self.assertIn('test/samples/sample11.txt', hitdocs)
        
        for hit in hits:
            if hit.docid == 'test/samples/sample3.txt':
                self.assertEqual(hit.char_offsets, [(31, 35)])
                self.assertEqual(hit.positions, [7])        
    

        #test terms not present in sample10.txt are not added to the index
        hits = index.get_entry('')
        self.assertEqual([], hits, "Expected no results for empty search term")

        hits = index.get_entry('pumpkin')
        self.assertEqual([], hits, "Expected no results for non-occuring term 'pumpkin'")
        index.clear()
        
    
    def test_index_string(self):
        """Test that we can index from a string"""
        
        
        index = alveo.Index()
        index.clear()
        
        text1 = "now is the winter of our discontent made glorious summer by this son of york"
        text2 = "now one two three"
        
        index.index_string("text1", text1)
        index.index_string("text2", text2)
        
        hits = index.get_entry('now')
        self.assertEqual(2, len(hits))
        
        hits = index.get_entry('two')
        self.assertEqual(1, len(hits))
        
        
    
    def test_clear_index(self):
        """Test that the clear method removes stuff from the index"""
                
        index = alveo.Index()

        for filename in self.documents:
            index.index_document(filename)
    
        hits = index.get_entry('the')

        self.assertGreater(len(hits), 0, "Expected some hits on 'the'")
        
        index.clear()
        
        newhits = index.get_entry('the')
        
        self.assertEqual(0, len(newhits), "Expected zero hits from cleared index")
        
    
    
    def test_alveo_index(self):
        import pyalveo 
        # fails due to invalid API key
        self.assertRaises(pyalveo.APIError, alveo.AlveoIndex, ("invalid key"))
        
        

        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.TextTestRunner(verbosity=2).run(unittest.makeSuite(Test))