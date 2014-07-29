"""
Created on 3/10/2013
Last updated on 21/11/2013

@author: Nicholas Lanfranca
"""

class IndexValue:
    """A class to hold the postings list for an inverted index."""
    
    def __init__(self, term, filename):
        """Sets the term for the posting list, as well as the filename."""
        self._term = term
        self._filename = filename
        self._char_offsets = []
        self._positions = []

    def add_char_offsets(self, char_offsets):
        """Adds char_offsets to the stored character offsets. char_offsets is a
list of the term's character offsets."""
        self._char_offsets.extend(char_offsets)

    def get_char_offsets(self):
        """Gets the character offsets, as a list."""
        return self._char_offsets

    def add_positions(self, positions):
        """Adds positions to the stored positions. positions is a list of the
term's positions."""
        self._positions.extend(positions)

    def get_positions(self):
        """Gets the positions, as a list."""
        return self._positions

    def get_filename(self):
        """Gets the filename."""
        return self._filename

    def get_term(self):
        """Gets the term that this object belongs to."""
        return self._term
