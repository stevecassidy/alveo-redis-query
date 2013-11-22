
class IndexValue:
    
    def __init__(self, token, filename):
        self._token = token
        self._filename = filename
        self._char_offsets = []
        self._positions = []

    def add_char_offsets(self, char_offsets):
        self._char_offsets.extend(char_offsets)

    def get_char_offsets(self):
        return self._char_offsets

    def add_positions(self, positions):
        self._positions.extend(positions)

    def get_positions(self):
        return self._positions

    def get_filename(self):
        return self._filename

    def get_token(self):
        return self._token
