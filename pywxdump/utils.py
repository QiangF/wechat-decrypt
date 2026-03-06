import hmac
import hashlib
import logging

wx_core_loger = logging.getLogger("wx_core")

def wx_core_error(func):
    """
    错误处理装饰器
    :param func:
    :return:
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            wx_core_loger.error(f"wx_core_error: {e}", exc_info=True)
            return None
    return wrapper


def verify_key(key, wx_db_path):
    """
    验证key是否正确
    """
    KEY_SIZE = 32
    DEFAULT_PAGESIZE = 4096
    DEFAULT_ITER = 64000
    with open(wx_db_path, "rb") as file:
        blist = file.read(5000)
    salt = blist[:16]
    pk = hashlib.pbkdf2_hmac("sha1", key, salt, DEFAULT_ITER, KEY_SIZE)
    first = blist[16:DEFAULT_PAGESIZE]
    mac_salt = bytes([(salt[i] ^ 58) for i in range(16)])
    pk = hashlib.pbkdf2_hmac("sha1", pk, mac_salt, 2, KEY_SIZE)
    hash_mac = hmac.new(pk, first[:-32], hashlib.sha1)
    hash_mac.update(b'\x01\x00\x00\x00')
    if hash_mac.digest() != first[-32:-12]:
        return False
    return True
