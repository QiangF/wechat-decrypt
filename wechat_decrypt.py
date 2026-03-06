from pywxdump import decryption

args = {
    "mode": "decrypt",
    # 密钥
    "key": "a91223dd702248fa96456cdd57e6bc8689d7c1f42bc1444c9e7e115bcb38270f",
    #数据库路径(目录or文件)
    "db_path": "/home/q/Documents/xwechat_files/F100001765807792_a28d/db_storage/favorite",
    "out_path": "/tmp/my_tmp/"  # 输出路径（必须是目录）[默认为当前路径下decrypted文件夹]
}

result = decryption.batch_decrypt(args["key"], args["db_path"], args["out_path"], True)
