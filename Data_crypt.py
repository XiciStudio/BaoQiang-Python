import zlib
import miniamf.amf3
import base64

def decodeData(data):
    a = miniamf.amf3.ByteArray()
    a.append(zlib.decompress(base64.b64decode((data.encode()))))
    return a.readObject()


def encodeData(data):
    a = miniamf.amf3.ByteArray()
    a.writeObject(data)
    return base64.b64encode(zlib.compress(a.encode()))