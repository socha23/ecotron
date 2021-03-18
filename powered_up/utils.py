from struct import pack, unpack

def as_byte(val):
    return pack("<B", val)

def as_int(bytes):
    return unpack("<B", bytes)[0]
