import enum

class Response(enum.Enum):
    OK = 0
    BAD_REQUEST = 1

    def encode(self):
        return b'a' + self.value.to_bytes(1, byteorder='big', signed=False)