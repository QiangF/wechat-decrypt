from pywxdump import decryption

args = {
    "mode": "decrypt",
    # 密钥
    "key": "a91223dd702248fa96456cdd57e6bc8689d7c1f42bc1444c9e7e115bcb38270f",
    # 数据库路径(目录or文件)
    "db_path": "/home/q/Documents/xwechat_files/F100001765807792_a28d/db_storage/favorite",
    # 输出路径（必须是目录）[默认为当前路径下decrypted文件夹]
    "out_path": "/tmp/my_tmp"
}

# result = decryption.batch_decrypt(args["key"], args["db_path"], args["out_path"], True)



import hmac
import hashlib
import os
from typing import Union, List
from Crypto.Cipher import AES

SQLITE_FILE_HEADER = "SQLite format 3\x00"  # SQLite文件头
KEY_SIZE = 32
DEFAULT_PAGESIZE = 4096
DEFAULT_ITER = 4000

key = "a91223dd702248fa96456cdd57e6bc8689d7c1f42bc1444c9e7e115bcb38270f"
db_storage_path = "/home/q/Documents/xwechat_files/F100001765807792_a28d/db_storage"

# db_path = "/home/q/Documents/xwechat_files/F100001765807792_a28d/db_storage/favorite/favorite.db"
# out_path = "/tmp/my_tmp"
# # password = key.encode()
# password = bytes.fromhex(key.strip())

# with open(db_path, "rb") as file:
#     blist = file.read()

# # 每一个数据库文件的开头16字节都保存了一段唯一且随机的盐值，作为HMAC的验证和数据的解密
# salt = blist[:16]
# first = blist[16:DEFAULT_PAGESIZE]
# if len(salt) != 16:
#     print(f"[-] db_path:'{db_path}' File Error!")
# mac_salt = bytes([(salt[i] ^ 58) for i in range(16)])
# byteHmac = hashlib.pbkdf2_hmac("sha1", password, salt, 64000, KEY_SIZE)
# mac_key = hashlib.pbkdf2_hmac("sha1", byteHmac, mac_salt, 2, KEY_SIZE)
# hash_mac = hmac.new(mac_key, blist[16:4064], hashlib.sha1)
# hash_mac.update(b'\x01\x00\x00\x00')

# if hash_mac.digest() != first[-32:-12]:
#     print(f"[-] Key Error! (key:'{key}'; db_path:'{db_path}'; out_path:'{out_path}' )")

# with open(out_path, "wb") as deFile:
#     deFile.write(SQLITE_FILE_HEADER.encode())
#     for i in range(0, len(blist), 4096):
#         tblist = blist[i:i + 4096] if i > 0 else blist[16:i + 4096]
#         deFile.write(AES.new(byteHmac, AES.MODE_CBC, tblist[-48:-32]).decrypt(tblist[:-48]))
#         deFile.write(tblist[-48:])



from pywxdump.WeChatDataAnalysis_decrypt import decrypt_wechat_databases

result = decrypt_wechat_databases(db_storage_path, key)
if result["status"] == "error":
    print(f"错误: {result['message']}")
else:
    print(f"解密完成: {result['message']}")
    print(f"输出目录: {result['output_directory']}")
