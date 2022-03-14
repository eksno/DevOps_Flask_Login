import traceback
from app.components import cipher

from app.components.cipher import AESCipher

cipher = AESCipher()

def exception_str(e):
    return str(type(e)) + ": " + str(e) + "\n" + '\n'.join(traceback.format_tb(e.__traceback__))

def encrypt_user_dict(user_dict):
    user_dict = {
        "id": cipher.encrypt(str(user_dict["id"])),
        "email": cipher.encrypt(user_dict["email"]),
        "username": cipher.encrypt(user_dict["username"]),
        "password": cipher.encrypt(user_dict["password"]),
    }
    return user_dict

def decrypt_user_dict(user_dict):
    user_dict = {
        "id": int(cipher.decrypt(user_dict["id"])),
        "email": cipher.decrypt(user_dict["email"]),
        "username": cipher.decrypt(user_dict["username"]),
        "password": cipher.decrypt(user_dict["password"]),
    }
    return user_dict