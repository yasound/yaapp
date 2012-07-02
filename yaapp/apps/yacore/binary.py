from struct import unpack_from

class BinaryData:
    def __init__(self, data):
        self.offset = 0
        self.data = data

    def get_int16(self):
        res = unpack_from('<h', self.data, self.offset)[0]
        self.offset = self.offset + 2
        return res

    def get_int32(self):
        res = unpack_from('<i', self.data, self.offset)[0]
        self.offset = self.offset + 4
        return res

    def get_tag(self):
        res = unpack_from('<4s', self.data, self.offset)[0]
        self.offset = self.offset + 4
        return res

    def get_string(self):
        size = self.get_int16()
        res = unpack_from('<' + str(size) + 's', self.data, self.offset)[0]
        self.offset = self.offset + size
        return res

    def is_done(self):
        return self.offset >= len(self.data)