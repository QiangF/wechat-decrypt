# wechat_decrypt.py from https://pypi.org/project/pywxdump

无法解密，错误信息：

    In [1]: %run wechat_decrypt.py
    ================================
    [-] Key Error! (key:'a91223dd702248fa96456cdd57e6bc8689d7c1f42bc1444c9e7e115bcb38270f'; db_path:'/home/q/Documents/xwechat_files/F100001765807792_a28d/db_storage/favorite/favorite.db'; out_path:'/tmp/my_tmp/./de_favorite.db' )
    [-] Key Error! (key:'a91223dd702248fa96456cdd57e6bc8689d7c1f42bc1444c9e7e115bcb38270f'; db_path:'/home/q/Documents/xwechat_files/F100001765807792_a28d/db_storage/favorite/favorite_fts.db'; out_path:'/tmp/my_tmp/./de_favorite_fts.db' )
    [-] Key Error! (key:'a91223dd702248fa96456cdd57e6bc8689d7c1f42bc1444c9e7e115bcb38270f'; db_path:'/home/q/Documents/xwechat_files/F100001765807792_a28d/db_storage/favorite/favorite_fts.db-wal'; out_path:'/tmp/my_tmp/./de_favorite_fts.db-wal' )
    [-] Key Error! (key:'a91223dd702248fa96456cdd57e6bc8689d7c1f42bc1444c9e7e115bcb38270f'; db_path:'/home/q/Documents/xwechat_files/F100001765807792_a28d/db_storage/favorite/favorite_fts.db-shm'; out_path:'/tmp/my_tmp/./de_favorite_fts.db-shm' )
    [-] Key Error! (key:'a91223dd702248fa96456cdd57e6bc8689d7c1f42bc1444c9e7e115bcb38270f'; db_path:'/home/q/Documents/xwechat_files/F100001765807792_a28d/db_storage/favorite/favorite.db-wal'; out_path:'/tmp/my_tmp/./de_favorite.db-wal' )
    [-] Key Error! (key:'a91223dd702248fa96456cdd57e6bc8689d7c1f42bc1444c9e7e115bcb38270f'; db_path:'/home/q/Documents/xwechat_files/F100001765807792_a28d/db_storage/favorite/favorite.db-shm'; out_path:'/tmp/my_tmp/./de_favorite.db-shm' )
    --------------------------------
    [+] 共 6 个文件, 成功 0 个, 失败 6 个


# wechat_decrypt.py from WeChatDataAnalysis
两个数据库无法全部解密，错误信息：

    2026-03-06 15:34:51 | INFO | pywxdump.WeChatDataAnalysis_decrypt | 开始解密数据库: /home/q/Documents/xwechat_files/F100001765807792_a28d/db_storage/message/message_fts.db
    2026-03-06 15:34:51 | INFO | pywxdump.WeChatDataAnalysis_decrypt | 读取文件大小: 10485760 bytes
    2026-03-06 15:34:51 | WARNING | pywxdump.WeChatDataAnalysis_decrypt | 页面 1006 HMAC验证失败
    ...
    2026-03-06 15:34:52 | INFO | pywxdump.WeChatDataAnalysis_decrypt | 解密完成: 成功 1005 页, 失败 1555 页
    2026-03-06 15:34:52 | INFO | pywxdump.WeChatDataAnalysis_decrypt | 解密文件大小: 4116480 bytes
    2026-03-06 15:34:52 | INFO | pywxdump.WeChatDataAnalysis_decrypt | 解密成功: F100001765807792_a28d/message_fts.db
    
    
    2026-03-06 15:34:55 | INFO | pywxdump.WeChatDataAnalysis_decrypt | 开始解密数据库: /home/q/Documents/xwechat_files/F100001765807792_a28d/db_storage/message/message_resource.db
    2026-03-06 15:34:55 | INFO | pywxdump.WeChatDataAnalysis_decrypt | 读取文件大小: 26214400 bytes
    2026-03-06 15:34:55 | WARNING | pywxdump.WeChatDataAnalysis_decrypt | 页面 259 HMAC验证失败
    ...
    2026-03-06 15:34:57 | INFO | pywxdump.WeChatDataAnalysis_decrypt | 解密完成: 成功 258 页, 失败 6142 页
    2026-03-06 15:34:57 | INFO | pywxdump.WeChatDataAnalysis_decrypt | 解密文件大小: 1056768 bytes
    2026-03-06 15:34:57 | INFO | pywxdump.WeChatDataAnalysis_decrypt | 解密成功: F100001765807792_a28d/message_resource.db
    
# 数据库名称
## Favorite
    FavItems：收藏的消息条目列表
    FavDataItem：收藏的具体数据。没有自习去看他的存储逻辑，不过大概可以确定以下两点
        即使只是简单收藏一篇公众号文章也会在 FavDataItem 中有一个对应的记录
        对于收藏的合并转发类型的消息，合并转发中的每一条消息在 FavDataItem 中都是一个独立的记录
    FavTags：为收藏内容添加的标签
