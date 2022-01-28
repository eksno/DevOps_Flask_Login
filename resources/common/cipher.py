import os
import base64
import logging

try:  # The crypto package depends on the library installed
    from Crypto import Random
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad
except ImportError:
    from Cryptodome import Random
    from Cryptodome.Cipher import AES
    from Cryptodome.Util.Padding import pad, unpad


__BLOCK_SIZE__ = 32


class AESCipher:
    def __init__(self, key=None):
        if key is not None:
            self.key = bytes(str(key), "utf-8")
        else:
            self.key = bytes(str(os.environ["KEY"]), "utf-8")

    def encrypt(self, raw):
        """
        Encodes data

        :param data: Data to be encoded
        :type data: str
        :returns:  string -- Encoded data
        """
        raw = bytes(pad(data_to_pad=raw.encode("utf-8"), block_size=__BLOCK_SIZE__))
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        encrypted = base64.b64encode(iv + cipher.encrypt(raw)).decode("utf-8")
        return encrypted

    def decrypt(self, enc):
        """
        Decodes data

        :param data: Data to be decoded
        :type data: str
        :returns:  string -- Decoded data
        """
        enc = base64.b64decode(enc)
        iv = enc[: AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted = unpad(
            padded_data=cipher.decrypt(enc[AES.block_size :]), block_size=__BLOCK_SIZE__
        ).decode("utf-8")
        return decrypted


def test_cipher(phrase="AESCipherTest"):
    key = "8aa9d5d4372eb78c865246e6ecd2bb36"

    logging.info("Testing AESCipher on phrase: " + phrase + " with key " + str(key))

    cipher = AESCipher(key=key)

    encrypted = cipher.encrypt(phrase)
    logging.info("Encrypted: " + str(encrypted))

    decrypted = cipher.decrypt(encrypted)
    if phrase == decrypted:
        logging.info("Decrypted: " + decrypted)
    else:
        logging.error(decrypted + " does not match phrase " + phrase)


def create_handlers():
    # Create handler
    c_handler = logging.StreamHandler()
    c_handler.setLevel(logging.DEBUG)

    # Create formatter and add it to handler
    c_format = logging.Formatter("%(name)s - %(levelname)s - %(message)s")

    # Apply formatter
    c_handler.setFormatter(c_format)

    return c_handler


if __name__ == "__main__":
    # Configure logging
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    c_handler = create_handlers()
    logger.addHandler(c_handler)
    test_cipher()
