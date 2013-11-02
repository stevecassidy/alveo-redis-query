
class IndexValue:
    
    def __init__(self, token, filename):
        self._token = token
        self._filename = filename
        self._char_offset_values = []

    def add_char_offset_value(self, char_offset_value):
        self._char_offset_values.extend(char_offset_value)

    def get_char_offset_values(self):
        return self._char_offset_values

    def get_filename(self):
        return self._filename

    def get_token(self):
        return self._token
