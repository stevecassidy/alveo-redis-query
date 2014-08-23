
import os
import unittest

import alveo_redis_query as alveo


class Test(unittest.TestCase):

    filePath = os.path.dirname(__file__)
    relativePath = "samples"
    absolutePath = os.path.join(filePath, relativePath)
    documents = [os.path.join(absolutePath,'sample1.txt'),
                os.path.join(absolutePath,'sample2.txt'),
                os.path.join(absolutePath,'sample3.txt'),
                os.path.join(absolutePath,'sample4.txt'),
                os.path.join(absolutePath,'sample5.txt'),
                os.path.join(absolutePath,'sample6.txt'),
                os.path.join(absolutePath,'sample7.txt'),
                os.path.join(absolutePath,'sample8.txt'),
                os.path.join(absolutePath,'sample9.txt'),
                os.path.join(absolutePath,'sample10.txt'),
                os.path.join(absolutePath,'sample11.txt'),
                os.path.join(absolutePath,'sample12.txt'),
                ]

    def test_tokenise(self):
        index = alveo.Index()
        
        filename = os.path.join(self.absolutePath,'sample12.txt')
        with open(filename, 'r') as f:
            text = f.read()
            
        correct_char_offsets = [[(113, 120)], [(121, 125)], [(41, 53)], [(104, 112)],
                                [(31, 40)], [(63, 69)], [(81, 96)], [(54, 55)], [(97, 103)],
                                [(56, 62), (126, 132)], [(20, 30)], [(5, 11)], [(12, 19)], [(70, 80)],
                                [(0, 4)]]
        correct_tokens = ['10.30am', '14.9', '234.43.65.87', '3254.543',
                          '3450.3050', '345gvr', '40rjero3orejr04', 'a',
                          'a23435', 'ahfc27', 'anti-intel', "didn't", "o'clock",
                          'sfn403vtjb', 'test']
        correct_positions = [[14], [15], [6], [13], [5], [9], [11], [7], [12], [8, 16], [4], [2], [3], [10], [1]]
        
        d = index._tokenise(filename, text)
        tokens = d.keys()
        tokens.sort()
        
        # test the length number of tokens
        self.assertEqual(len(tokens), len(correct_tokens),
                         "Wrong number of tokens. Expected %d, got %d" %
                         (len(correct_tokens), len(tokens)))
        
        for i in range(len(tokens)):
            # test the tokens
            self.assertEqual(tokens[i], correct_tokens[i], "Expected %s, got %s" %
                         (correct_tokens[i], tokens[i]))

            char_offsets = d[tokens[i]].char_offsets
            positions = d[tokens[i]].positions
            
            # test the offsets
            self.assertEqual(char_offsets, correct_char_offsets[i], "Expected %s, got %s" %
                         (correct_char_offsets[i], char_offsets))
            
            # test the positions
            self.assertEqual(positions, correct_positions[i], "Expected %s, got %s" %
                         (correct_positions[i], positions))

    def test_index_documents(self):

        index = alveo.Index()
        index.clear()

        for filename in self.documents:
            index._index_document(filename)
        
        term = 'this'
        
        hits = index._get_entry(term)
        
        # test the number of documents containing the term
        self.assertEqual(3, len(hits), "Expected three documents to match query for 'this'")
        
        hitdocs = [hit.docid for hit in hits]
        self.assertIn(os.path.join(self.absolutePath,'sample3.txt'), hitdocs)
        self.assertIn(os.path.join(self.absolutePath,'sample6.txt'), hitdocs)
        self.assertIn(os.path.join(self.absolutePath,'sample11.txt'), hitdocs)
        
        for hit in hits:
            # test the result for term 'this' in document 'sample3'
            if hit.docid == os.path.join(self.absolutePath,'sample3.txt'):
                self.assertEqual(hit.char_offsets, [(31, 35)])
                self.assertEqual(hit.positions, [7])        
    

        #test terms not present in sample10.txt are not added to the index
        hits = index._get_entry('')
        self.assertEqual([], hits, "Expected no results for empty search term")

        hits = index._get_entry('pumpkin')
        self.assertEqual([], hits, "Expected no results for non-occuring term 'pumpkin'")
        index.clear()
        
    
    def test_index_string(self):
        """Test that we can index from a string"""
        
        
        index = alveo.Index()
        index.clear()
        
        text1 = "now is the winter of our discontent made glorious summer by this son of york"
        text2 = "now one two three"
        
        index._index_string("text1", text1)
        index._index_string("text2", text2)
        
        hits = index._get_entry('now')
        self.assertEqual(2, len(hits))
        
        hits = index._get_entry('two')
        self.assertEqual(1, len(hits))
        
        
    
    def test_clear_index(self):
        """Test that the clear method removes stuff from the index"""
                
        index = alveo.Index()

        for filename in self.documents:
            index._index_document(filename)
    
        hits = index._get_entry('the')
        
        # test number of results before and after performing clear operation
        self.assertGreater(len(hits), 0, "Expected some hits on 'the'")
        
        index.clear()
        
        newhits = index._get_entry('the')
        
        self.assertEqual(0, len(newhits), "Expected zero hits from cleared index")
        
    
    
    def test_alveo_index(self):
        import pyalveo 
        # fails due to invalid API key
        self.assertRaises(pyalveo.APIError, alveo.AlveoIndex, ("invalid key"))
        
        
    def test_and_query(self):
        """Test AND functionality"""
        index = alveo.Index()
        index.clear()
        
        for filename in self.documents:
            index._index_document(filename)
        
        result = index._AND_query(["information", "many"])
        
        #test number of results
        self.assertEqual(len(result), 1, "expected exactly 1 indexValue")
        
        # test the documents
        correct_doc = os.path.join(self.absolutePath,'sample10.txt')
        self.assertEqual(result[0].docid, correct_doc, "expected " + correct_doc + " got " + result[0].docid)
        
        # test the number of occurrences
        correct_offsets_sum = 7
        self.assertEqual(len(result[0].char_offsets), correct_offsets_sum, "expected 7 occurrences got " + str(len(result[0].char_offsets)))
        
    def test_mark_check(self):
        """Test marking an item as indexed and checking the indexed status of the item"""
        index = alveo.AlveoIndex("place-your-apikey-here")
        index._mark_item_indexed("name", "url1")
        index._mark_item_indexed("name", "url2")
        result = index._check_item_url("name", "url1")
        
        # test indexed items
        self.assertEqual(result, True, "Expected to mark url1 under name")
        result = index._check_item_url("name", "url2")
        self.assertEqual(result, True, "Expected to mark url2 under name")
        result = index._check_item_url("name", "url3")
        
        # test not indexed items
        self.assertEqual(result, False, "Didn't expect to mark url3 under name")
        result = index._check_item_url("name1", "url1")
        self.assertEqual(result, False, "Didn't expect to mark any url under name1")
        index.clear()
        result = index._check_item_url("name", "url1")
        
        # test clear function
        self.assertEqual(result, False, "Expected to remove all urls")
        
    def test_proximity_query(self):
        """Test proximity query"""
        index = alveo.Index()
        index.clear()
        
        for filename in self.documents:
            index._index_document(filename)
            
        # test number of results
        result = index._proximity_query("information", "retrieval")
        self.assertEqual(len(result), 1, "expected exactly 1 indexValue, got " + str(len(result)))
        
        # test the document
        correct_doc = os.path.join(self.absolutePath,'sample10.txt')
        self.assertEqual(result[0].docid, correct_doc, "expected " + correct_doc + " got " + result[0].docid)
        
        # test number of offsets
        correct_offsets_sum = 4
        self.assertEqual(len(result[0].char_offsets), correct_offsets_sum, "expected 4 occurrences got " + str(len(result[0].char_offsets)))
        
        # test different proximity
        result = index._proximity_query("information", "systems", minimal_proximity=2)
        self.assertEqual(len(result), 1, "expected exactly 1 indexValue, got " + str(len(result)))
        
        # test the document
        correct_doc = os.path.join(self.absolutePath,'sample10.txt')
        self.assertEqual(result[0].docid, correct_doc, "expected " + correct_doc + " got " + result[0].docid)
        
        # test number of offsets
        correct_offsets_sum = 2
        self.assertEqual(len(result[0].char_offsets), correct_offsets_sum, "expected 2 occurrences got " + str(len(result[0].char_offsets)))
        
        # test order with no match
        result = index._proximity_query("information", "Automated", order=True)
        self.assertEqual(len(result), 0, "expected no indexValues, got " + str(len(result)))
        
        # test order with match
        result = index._proximity_query("Automated", "information", order=True)
        self.assertEqual(len(result), 1, "expected exactly 1 indexValue, got " + str(len(result)))
        
        # test the document
        correct_doc = os.path.join(self.absolutePath,'sample10.txt')
        self.assertEqual(result[0].docid, correct_doc, "expected " + correct_doc + " got " + result[0].docid)
        
        # test number of offsets
        correct_offsets_sum = 2
        self.assertEqual(len(result[0].char_offsets), correct_offsets_sum, "expected 2 occurrences got " + str(len(result[0].char_offsets)))
        
            
            
            
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.TextTestRunner(verbosity=2).run(unittest.makeSuite(Test))