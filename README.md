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


# wechat_decrypt.py from https://github.com/LifeArchiveProject/WeChatDataAnalysis
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
    
# Favorite 数据库
FavItems：收藏的消息条目列表
FavDataItem：收藏的具体数据。没有自习去看他的存储逻辑，不过大概可以确定以下两点
    即使只是简单收藏一篇公众号文章也会在 FavDataItem 中有一个对应的记录
    对于收藏的合并转发类型的消息，合并转发中的每一条消息在 FavDataItem 中都是一个独立的记录
FavTags：为收藏内容添加的标签

执行 python WeChat_Favorites_Export.py 导出结果在WeChat_Favorites_Export.txt中。
注意：后期收藏内容有变，若要将db文件单独复制出来重新执行py导出操作时，需将favorites.db、favorites.db-shm、favorites.db-wal这三个文件放置在同一路径下，打开数据库并禁用密码，新增数据会保存在favorites.db-shm、favorites.db-wal中，如果只拷贝favorites.db并打开会发现还是之前的数据没有变化

Contact - wccontact_new2.db - 好友信息
Group - group_new.db - 群聊和群成员信息
Message - {msg_0.db - msg_9.db} - 聊天记录和公众号文章
Favorites - favorites.db - 收藏

首先来看联系人数据库 wccontact_new2.db，这里主要就是一张表 WCContact，这里面存储了我们加的微信好友和关注的公众号的信息，主要是昵称和微信号 m_nsUsrName。一般公众号以 gh_ 开头。这里的 m_nsUsrName 非常重要，因为聊天数据库里的表名都是 md5 编码后的 m_nsUsrName。比如公众号 广发证券研究 的 m_nsUsrName 为 gh_24e4252623cf，md5 编译后即为 41cbc56f1e10ab139339a40a4df2132d，因此聊天记录数据库里的 Chat_41cbc56f1e10ab139339a40a4df2132d 即为这个公众号的全部历史信息。

favorites.db 里面有 8 张表，其中最重要的是两个，FavoriteItemTable 和 FavoriteSearchTable。
FavoriteSearchTable 给了收藏的标题和 localID。
FavoriteItemTable 给了收藏时间戳，收藏内容链接，以及收藏内容来源用户等，并且可以和 FavoriteSearchTable 通过 localID 互相索引。

https://github.com/WQdream/wx-cache-read
127M	db_storage/message
23M	db_storage/contact

17M	db_storage/favorite
21M	business/favorite/thumb
23M	business/favorite/mid

67M	business/favorite/data
70M	cache

# related
https://github.com/bugtest/wechat-favorites-export
https://github.com/gzxmren/wechat_gzh_downloader

gui automation
https://github.com/Vincentlz/WchatCollection
https://github.com/Hello-Mr-Crab/pywechat
https://github.com/LAVARONG/wechat-automation-api
https://github.com/pmhw/winautowx

# 视频号
https://github.com/nobiyou/wx_channel

# todo
1. 抓取收藏的链接，形成知识库
https://github.com/git-zyyang/reading-inbox
2. 抓取点赞收藏的视频并下载
