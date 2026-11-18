"""Decode a Vassal savedGame (!VCSK obfuscation) to text."""
import sys
def decode(b: bytes) -> str:
    if not b.startswith(b'!VCSK'):
        return b.decode('utf-8', 'replace')
    key = int(b[5:7], 16)
    body = b[7:]
    out = bytearray(int(body[i:i+2], 16) ^ key for i in range(0, len(body) - 1, 2))
    return out.decode('utf-8', 'replace')
if __name__ == '__main__':
    sys.stdout.write(decode(open(sys.argv[1], 'rb').read()))
