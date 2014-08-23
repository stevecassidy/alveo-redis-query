
Alveo Redis Query
#################

Alveo Redis Query is a project written in Python_ that provides
a specialised search engine that works on top of Alveo_.

Requirements
************

You need to install pyalveo_ and Redis_ prior to install this project.

Download
********

You can get the latest version from alveo_redis_query_'s github.

Installing
**********

Use ``setup.py``::

   sudo python setup.py install
   
Demo
****

After installing, run the main.py module in demo folder and type http://localhost:8080/ in your
browser. You need to put your API key in the identified place in main and prepare modules to get the demo to work.
Run prepare module to index the gum-tree itemList then run demo.

Known Issues
************

_process_query can recognise single word and a set of words seperated by 'and'. 

Documentation
*************

Index Objects
=============
*class alveo_redis_query.Index([db])*

Returns a new Index object.
Index is a class that provides basic tools to create, stroe, and query an index entry.
All index entries are stored on Redis_ server.
This class is not aimed to instantiate directly; AlveoIndex_, a subclass of Index, is
designed for this purpose to be the public interface of the project.

The argument , db, is the number of the database on which each instance of the class operates.
This makes it possible to serve several users, each with a specific database instance.

Methods
-------
+-------------------------------------------------------------+-------------------------------------------------------------------------+
| Method                                                      | Description                                                             |
+=============================================================+=========================================================================+
||*__init__([db])*                                            |Constructor of the class Index_.                                         |
+-------------------------------------------------------------+-------------------------------------------------------------------------+
||*clear()*                                                   |Clears all entries from the database for this instance.                  |
+-------------------------------------------------------------+-------------------------------------------------------------------------+
||*execute_query(query)*                                      |Processes the query string and performs a proper action.                 |
|                                                             |Returns list of all values stored on the database for the given query.   |
+-------------------------------------------------------------+-------------------------------------------------------------------------+
||*_AND_operator(working_list, [group])*                      |Performs AND operation on all given indexLists.                          |
|                                                             |Optional group argument indicates whether the tokens are considered as   |
|                                                             |one group in the query.                                                  |
|                                                             |Returns list of IndexValue_ objects.                                     |
+-------------------------------------------------------------+-------------------------------------------------------------------------+
||*_AND_query(terms, [group])*                                |Calculate the intersection of entries for all given terms.               |
|                                                             |Optional group argument indicates whether the terms are considered as    |
|                                                             |one group in the query.                                                  |
|                                                             |Returns list of IndexValue_ objects.                                     |
+-------------------------------------------------------------+-------------------------------------------------------------------------+
||*_get_entry(term)*                                          |Returns all values stored on the database for the given token,           |
|                                                             |as a defaultdict.                                                        |
+-------------------------------------------------------------+-------------------------------------------------------------------------+
||*_get_proximity_offsets(index_value_1, index_value_2*       |Performs the proximity operation on positions and returns the offsets.   |
||*,[minimal_proximity], [order])*                            |                                                                         |
+-------------------------------------------------------------+-------------------------------------------------------------------------+
||*_index_document(filename)*                                 |Creates and stores index entries for every token in the file's content.  |
+-------------------------------------------------------------+-------------------------------------------------------------------------+
||*_index_string(docid, s)*                                   |Creates and stores index entries for every token in the string.          |
+-------------------------------------------------------------+-------------------------------------------------------------------------+
||*_NOT_operator(index_list1, index_list2)*                   |Performs NOT operation on the given indexLists.                          |
|                                                             |The operation excludes tokens of indexlist2 from indexlist1.             |
|                                                             |Returns list of IndexValue_ objects.                                     |
+-------------------------------------------------------------+-------------------------------------------------------------------------+
||*_OR_operator(working_list, [group])*                       |Performs OR operation on all given indexLists.                           |
|                                                             |Optional group argument indicates whether the tokens are considered as   |
|                                                             |one group in the query.                                                  |
|                                                             |Returns list of IndexValue_ objects.                                     |
+-------------------------------------------------------------+-------------------------------------------------------------------------+
||*_process_query(query)*                                     |Processes the query string and performs proper actions.                  |
+-------------------------------------------------------------+-------------------------------------------------------------------------+
||*_proximity_operator(index_list1, index_list2,*             |Performs proximity operation on the given indexLists.                    |
||*[minimal_proximity], [order])*                             |The result includes IndexValue_ objects documents of which contain       |
|                                                             |tokens of bothindexLists whitin a given distance range with thw given    |
|                                                             |order.                                                                   |
|                                                             |Returns list of IndexValue_ objects.                                     |
+-------------------------------------------------------------+-------------------------------------------------------------------------+
||*_proximity_query(term1, term2, [minimal_proximity],*       |Performs proximity operation on the given terms.                         |
||*[order])*                                                  |It uses _proximity_operator to return the results.                       |
+-------------------------------------------------------------+-------------------------------------------------------------------------+
||*_tokenise(docid, text)*                                    |Processes the given text and identifies all tokens.                      |
|                                                             |Creates an IndexValue_ object for each token.                            |
|                                                             |Returns list of IndexValue objects.                                      |
+-------------------------------------------------------------+-------------------------------------------------------------------------+
||*_XOR_operator(index_list1, index_list2)*                   |Performs XOR operation on the given indexLists.                          |
|                                                             |The result includes tokens of both indexLists excluding tokens that are  |
|                                                             |common in both.                                                          |
|                                                             |Returns list of IndexValue_ objects.                                     |
+-------------------------------------------------------------+-------------------------------------------------------------------------+

AlveoIndex Objects
==================
*class alveo_redis_query.AlveoIndex(api_key, [db])*

Returns a new AlveoIndex object.
AlveoIndex is a subclass of _Index that provides extra tools to work with pyalveo API.
You can instanciate this class by passing an API key from Alveo_. Then you will be able to index the collections
and start searching.

The argument , api_key, is the string that you can obtain from Alveo_'s Website.

Methods
-------
+-------------------------------------------------------------+-------------------------------------------------------------------------+
| Method                                                      | Description                                                             |
+=============================================================+=========================================================================+
||*__init__(api_key, [db])*                                   |Constructor of the class AlveoIndex_.                                    |
+-------------------------------------------------------------+-------------------------------------------------------------------------+
||*index_item_list_by_name(item_list_name)*                   |Indexes an itemList specified by name.                                   |
+-------------------------------------------------------------+-------------------------------------------------------------------------+
||*index_item_list([given_item_list])*                        |Indexes a specified itemList or the entire collection if no itemList     |
|                                                             |specified.                                                               |
+-------------------------------------------------------------+-------------------------------------------------------------------------+
||*_check_item_url(item_list_name, item_url)*                 |Checks if an item has already been indexed.                              |
+-------------------------------------------------------------+-------------------------------------------------------------------------+
||*_combine(ownerships)*                                      |Creates a single list of sources from sources with different ownerships. |
+-------------------------------------------------------------+-------------------------------------------------------------------------+
||*_get_text_for_results(index_values, text_range,*           |Gets the text for the IndexValue_ objects in the given list.             |
||*decoration)*                                               |Argument text_range is a tuple indicating the range of characters before |
|                                                             |and after the token.                                                     |
|                                                             |Decoration is a boolean indicating whether to decorate the tokens.       |
+-------------------------------------------------------------+-------------------------------------------------------------------------+
||*_mark_item_indexed(item_list_name, item_url)*              |Marks an item as indexed by inserting an entry for that item on Redis_   |
+-------------------------------------------------------------+-------------------------------------------------------------------------+

IndexValue Objects
==================
*class alveo_redis_query.IndexValue([token], [docid])*

Returns a new IndexValue object.
IndexValue is a class to represent an entry to Redis_. This class also might be used to represent offsets of 
more than one token in a document for querying purposes.

Methods
-------
+-------------------------------------------------------------+-------------------------------------------------------------------------+
| Method                                                      | Description                                                             |
+=============================================================+=========================================================================+
||*__init__([token], [docid])*                                |Constructor of the class IndexValue_.                                    |
+-------------------------------------------------------------+-------------------------------------------------------------------------+
||*add_char_offsets(value)*                                   |Adds a list of character offsets to the instace's list of offsets.       |
+-------------------------------------------------------------+-------------------------------------------------------------------------+
||*add_positions(value)*                                      |Adds a list of positions to the instace's list of positions.             |
+-------------------------------------------------------------+-------------------------------------------------------------------------+
||*add_token(value)*                                          |Adds a list of tokens to the instace's list of tokens.                   |
+-------------------------------------------------------------+-------------------------------------------------------------------------+

Properties
----------
+-------------------------------------------------------------+-------------------------------------------------------------------------+
| Property                                                    | Description                                                             |
+=============================================================+=========================================================================+
||*char_offsets*                                              | *Read Only*                                                             |
|                                                             |List of character offsets within the document representing               |
|                                                             |the location of tokens by index numbers.                                 |
+-------------------------------------------------------------+-------------------------------------------------------------------------+
||*docid*                                                     |Name of the document.                                                    |
+-------------------------------------------------------------+-------------------------------------------------------------------------+
||*positions*                                                 | *Read Only*                                                             |
|                                                             |List of positions within the document representing  the location         |
|                                                             |of tokens by number of words from the start of the document.             |
+-------------------------------------------------------------+-------------------------------------------------------------------------+
||*token*                                                     | *Read Only*                                                             |
|                                                             |List of tokens within the document.                                      |
+-------------------------------------------------------------+-------------------------------------------------------------------------+



.. _alveo_redis_query: https://github.com/stevecassidy/alveo-redis-query
.. _pyalveo: https://github.com/Alveo/pyhcsvlab
.. _Alveo: http://alveo.edu.au/
.. _Python: https://www.python.org/
.. _Redis: http://redis.io/
