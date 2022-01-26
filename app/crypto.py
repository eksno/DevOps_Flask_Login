import base64
import base64
import hashlib
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

class AESCipher:
    def __init__(self, ) -> None:
        key = None
