"""
微信收藏同步模块
从微信PC版本地数据库中读取收藏内容，同步到NexusMind知识库
"""

import os
import sqlite3
import json
import hashlib
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import asyncio

logger = logging.getLogger(__name__)

class WeChatFavoritesSync:
    def __init__(self, wechat_user_path: str = None):
        # 如果提供了指定路径，直接使用；否则尝试自动查找
        if wechat_user_path:
            self.wechat_data_path = wechat_user_path
            logger.info(f"使用指定的微信用户路径: {self.wechat_data_path}")
        else:
            self.wechat_data_path = self._find_wechat_data_path()
        self.sync_record_file = "wechat_sync_record.json"
        
    def _find_wechat_data_path(self) -> Optional[str]:
        """查找微信数据目录"""
        try:
            logger.info("开始查找微信数据目录...")
            
            # Windows微信数据路径
            appdata = os.getenv('APPDATA')
            if not appdata:
                logger.error("无法获取APPDATA环境变量")
                return None
            
            logger.info(f"APPDATA路径: {appdata}")
            
            # 尝试多个可能的微信路径
            possible_wechat_paths = [
                os.path.join(os.path.expanduser('~'), 'Documents', 'WeChat Files'),  # 优先检查Documents路径
                os.path.join(appdata, 'Tencent', 'WeChat'),
                os.path.join(appdata, 'WeChat'),
                os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming', 'Tencent', 'WeChat'),
            ]
            
            wechat_base = None
            for path in possible_wechat_paths:
                logger.info(f"检查路径: {path}")
                if os.path.exists(path):
                    wechat_base = path
                    logger.info(f"找到微信基础目录: {wechat_base}")
                    break
            
            if not wechat_base:
                logger.error("未找到微信基础目录，请确认微信已安装")
                return None
            
            # 列出微信基础目录的内容
            try:
                base_contents = os.listdir(wechat_base)
                logger.info(f"微信基础目录内容: {base_contents}")
            except Exception as e:
                logger.error(f"无法读取微信基础目录: {e}")
                return None
            
            # 查找用户目录（通常是一个随机字符串或微信号）
            user_dirs = []
            for item in base_contents:
                item_path = os.path.join(wechat_base, item)
                if os.path.isdir(item_path):
                    # 检查是否是用户数据目录（包含Msg子目录或其他微信数据文件）
                    possible_data_paths = [
                        os.path.join(item_path, 'Msg'),
                        os.path.join(item_path, 'Data'),
                        os.path.join(item_path, 'FileStorage'),
                        os.path.join(item_path, 'Backup')
                    ]
                    
                    # 如果包含任何一个数据目录，就认为是用户目录
                    if any(os.path.exists(path) for path in possible_data_paths):
                        user_dirs.append(item)
                        logger.info(f"找到可能的用户目录: {item}")
                        
                        # 列出用户目录的内容
                        try:
                            user_contents = os.listdir(item_path)
                            logger.info(f"用户目录 {item} 内容: {user_contents}")
                        except Exception as e:
                            logger.debug(f"无法读取用户目录内容: {e}")
            
            if not user_dirs:
                logger.error("未找到包含Msg目录的用户数据目录")
                logger.info("请确认微信已登录并有聊天记录")
                return None
            
            # 使用第一个找到的用户目录
            selected_user = user_dirs[0]
            user_path = os.path.join(wechat_base, selected_user)
            logger.info(f"选择用户目录: {user_path}")
            
            # 验证目录结构
            msg_path = os.path.join(user_path, 'Msg')
            if os.path.exists(msg_path):
                msg_contents = os.listdir(msg_path)
                logger.info(f"Msg目录内容: {msg_contents}")
            
            return user_path
            
        except Exception as e:
            logger.error(f"查找微信数据路径失败: {e}")
            return None
    
    def _get_favorites_db_path(self) -> Optional[str]:
        """获取微信收藏数据库路径"""
        if not self.wechat_data_path:
            return None
        
        logger.info(f"在用户目录中查找收藏数据库: {self.wechat_data_path}")
        
        # 尝试多种可能的数据库路径
        possible_db_paths = [
            # 标准路径
            os.path.join(self.wechat_data_path, 'Msg', 'FTSContact.db'),
            os.path.join(self.wechat_data_path, 'Msg', 'MicroMsg.db'),
            os.path.join(self.wechat_data_path, 'Msg', 'Multi', 'MSG0.db'),
            
            # 收藏相关的数据库
            os.path.join(self.wechat_data_path, 'Msg', 'FavItems.db'),
            os.path.join(self.wechat_data_path, 'Msg', 'Favorites.db'),
            os.path.join(self.wechat_data_path, 'Data', 'FavItems.db'),
            os.path.join(self.wechat_data_path, 'Data', 'Favorites.db'),
            
            # 其他可能的位置
            os.path.join(self.wechat_data_path, 'config', 'FavItems.db'),
            os.path.join(self.wechat_data_path, 'db', 'FavItems.db'),
        ]
        
        # 检查每个可能的路径
        for db_path in possible_db_paths:
            logger.info(f"检查数据库路径: {db_path}")
            if os.path.exists(db_path):
                logger.info(f"找到数据库文件: {db_path}")
                return db_path
        
        # 如果没有找到，尝试搜索整个用户目录
        logger.info("未找到标准数据库文件，开始搜索整个用户目录...")
        try:
            found_databases = []
            for root, dirs, files in os.walk(self.wechat_data_path):
                for file in files:
                    if file.endswith('.db'):
                        db_path = os.path.join(root, file)
                        logger.info(f"找到数据库文件: {db_path}")
                        
                        # 尝试打开数据库验证
                        try:
                            conn = sqlite3.connect(db_path)
                            cursor = conn.cursor()
                            
                            # 检查是否包含收藏相关的表
                            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                            tables = [row[0] for row in cursor.fetchall()]
                            logger.info(f"数据库 {file} 包含的表: {tables}")
                            
                            # 记录所有可用的数据库
                            found_databases.append({
                                'path': db_path,
                                'file': file,
                                'tables': tables
                            })
                            
                            # 如果包含收藏相关的表，优先使用
                            if any(keyword in table.lower() for table in tables for keyword in ['fav', 'favorite']):
                                conn.close()
                                logger.info(f"选择包含收藏表的数据库: {db_path}")
                                return db_path
                            
                            conn.close()
                            
                        except Exception as e:
                            logger.debug(f"无法打开数据库 {db_path}: {e}")
                            continue
            
            # 如果没有找到包含收藏表的数据库，尝试使用其他数据库
            logger.info(f"找到 {len(found_databases)} 个可用数据库")
            for db_info in found_databases:
                logger.info(f"数据库: {db_info['file']}, 表: {db_info['tables']}")
                
                # 尝试使用包含消息相关表的数据库
                if any(keyword in table.lower() for table in db_info['tables'] for keyword in ['msg', 'message', 'chat']):
                    logger.info(f"尝试使用消息数据库: {db_info['path']}")
                    return db_info['path']
            
            # 如果还是没有找到合适的，使用第一个可用的数据库
            if found_databases:
                logger.info(f"使用第一个可用数据库: {found_databases[0]['path']}")
                return found_databases[0]['path']
                            
        except Exception as e:
            logger.error(f"搜索数据库文件时出错: {e}")
        
        logger.error("未找到可用的微信数据库文件")
        return None  
  
    def _load_sync_record(self) -> Dict[str, Any]:
        """加载同步记录"""
        try:
            if os.path.exists(self.sync_record_file):
                with open(self.sync_record_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"加载同步记录失败: {e}")
        
        return {
            'last_sync_time': None,
            'last_favorite_id': None,
            'synced_hashes': []
        }
    
    def _save_sync_record(self, record: Dict[str, Any]):
        """保存同步记录"""
        try:
            with open(self.sync_record_file, 'w', encoding='utf-8') as f:
                json.dump(record, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存同步记录失败: {e}")
    
    def _generate_content_hash(self, content: str) -> str:
        """生成内容哈希值"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _extract_favorites_from_db(self) -> List[Dict[str, Any]]:
        """从微信数据库中提取收藏内容"""
        # 搜索所有可能的数据库文件
        all_db_files = self._find_all_database_files()
        if not all_db_files:
            logger.error("未找到任何数据库文件")
            return []
        
        favorites = []
        
        # 尝试每个数据库文件
        for db_path in all_db_files:
            try:
                logger.info(f"尝试打开数据库: {db_path}")
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # 首先列出数据库中的所有表
                try:
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = [row[0] for row in cursor.fetchall()]
                    logger.info(f"数据库 {os.path.basename(db_path)} 中的所有表: {tables}")
                    
                    # 查看每个表的结构
                    for table in tables:
                        try:
                            cursor.execute(f"PRAGMA table_info({table});")
                            columns = cursor.fetchall()
                            logger.info(f"表 {table} 的结构: {columns}")
                            
                            # 查看表中的数据量
                            cursor.execute(f"SELECT COUNT(*) FROM {table};")
                            count = cursor.fetchone()[0]
                            logger.info(f"表 {table} 包含 {count} 条记录")
                            
                            # 如果表名包含收藏相关关键词，查看前几条数据
                            if any(keyword in table.lower() for keyword in ['fav', 'favorite', 'collect']):
                                logger.info(f"发现可能的收藏表: {table}")
                                cursor.execute(f"SELECT * FROM {table} LIMIT 3;")
                                sample_rows = cursor.fetchall()
                                if sample_rows:
                                    column_names = [description[0] for description in cursor.description]
                                    logger.info(f"表 {table} 的列名: {column_names}")
                                    for i, row in enumerate(sample_rows):
                                        logger.info(f"表 {table} 样本数据 {i+1}: {dict(zip(column_names, row))}")
                            
                        except sqlite3.Error as e:
                            logger.debug(f"无法查看表 {table}: {e}")
                            continue
                    
                    # 尝试从这个数据库提取收藏数据
                    db_favorites = self._try_extract_from_database(cursor, tables, os.path.basename(db_path))
                    if db_favorites:
                        favorites.extend(db_favorites)
                        logger.info(f"从数据库 {os.path.basename(db_path)} 提取到 {len(db_favorites)} 条收藏")
                        
                except sqlite3.Error as e:
                    logger.error(f"无法处理数据库 {os.path.basename(db_path)}: {e}")
                    
                conn.close()
                
            except Exception as e:
                logger.error(f"无法打开数据库 {db_path}: {e}")
                continue
        
        logger.info(f"总共提取到 {len(favorites)} 条收藏记录")
        return favorites
    
    def _find_all_database_files(self) -> List[str]:
        """查找所有数据库文件"""
        db_files = []
        try:
            logger.info(f"搜索数据库文件: {self.wechat_data_path}")
            for root, dirs, files in os.walk(self.wechat_data_path):
                for file in files:
                    if file.endswith('.db'):
                        db_path = os.path.join(root, file)
                        db_files.append(db_path)
                        logger.info(f"找到数据库文件: {db_path}")
        except Exception as e:
            logger.error(f"搜索数据库文件时出错: {e}")
        
        return db_files
    
    def _try_extract_from_database(self, cursor, tables: List[str], db_name: str) -> List[Dict[str, Any]]:
            
        """尝试从指定数据库提取收藏数据"""
        favorites = []
        
        # 尝试不同的表结构（微信版本不同，表结构可能不同）
        possible_queries = [
            # 尝试查询收藏表
            "SELECT * FROM FavItems ORDER BY createTime DESC",
            "SELECT * FROM Favorites ORDER BY time DESC", 
            "SELECT * FROM FavoriteItems ORDER BY createTime DESC",
            "SELECT * FROM FavObject ORDER BY createTime DESC",
            "SELECT * FROM FavoriteObject ORDER BY createTime DESC",
        ]
        
        # 如果发现了包含收藏关键词的表，也尝试查询
        for table in tables:
            if any(keyword in table.lower() for keyword in ['fav', 'favorite', 'collect']) and table not in ['FavItems', 'Favorites', 'FavoriteItems']:
                possible_queries.append(f"SELECT * FROM {table} ORDER BY rowid DESC")
        
        for query in possible_queries:
            try:
                logger.info(f"在数据库 {db_name} 中尝试查询: {query}")
                cursor.execute(query)
                rows = cursor.fetchall()
                
                if rows:
                    # 获取列名
                    columns = [description[0] for description in cursor.description]
                    logger.info(f"查询成功，找到 {len(rows)} 条记录，列名: {columns}")
                    
                    for row in rows:
                        favorite_data = dict(zip(columns, row))
                        favorites.append(favorite_data)
                    
                    logger.info(f"从数据库 {db_name} 提取到 {len(favorites)} 条收藏记录")
                    break
                    
            except sqlite3.Error as e:
                logger.debug(f"查询失败: {query}, 错误: {e}")
                continue
        
        return favorites
    
    def _parse_favorite_content(self, favorite_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """解析收藏内容"""
        try:
            # 根据微信数据库结构解析内容
            # 注意：实际的字段名可能因微信版本而异
            
            content = ""
            title = ""
            source_type = "微信收藏"
            create_time = None
            
            # 尝试提取不同字段的内容
            possible_content_fields = ['content', 'xml', 'data', 'text', 'msg']
            possible_title_fields = ['title', 'name', 'subject']
            possible_time_fields = ['createTime', 'time', 'timestamp']
            
            # 提取内容
            for field in possible_content_fields:
                if field in favorite_data and favorite_data[field]:
                    content = str(favorite_data[field])
                    break
            
            # 提取标题
            for field in possible_title_fields:
                if field in favorite_data and favorite_data[field]:
                    title = str(favorite_data[field])
                    break
            
            # 提取时间
            for field in possible_time_fields:
                if field in favorite_data and favorite_data[field]:
                    create_time = favorite_data[field]
                    break
            
            if not content and not title:
                return None
            
            # 如果没有标题，从内容中提取
            if not title and content:
                title = content[:50] + "..." if len(content) > 50 else content
            
            # 清理和格式化内容
            if content:
                # 如果是XML格式，尝试解析
                if content.startswith('<?xml') or content.startswith('<msg'):
                    content = self._parse_xml_content(content)
            
            return {
                'title': title,
                'content': content,
                'source_type': source_type,
                'create_time': create_time,
                'original_data': favorite_data
            }
            
        except Exception as e:
            logger.error(f"解析收藏内容失败: {e}")
            return None
    
    def _parse_xml_content(self, xml_content: str) -> str:
        """解析微信XML格式的收藏内容"""
        try:
            import xml.etree.ElementTree as ET
            
            # 清理XML内容
            xml_content = xml_content.replace('&', '&amp;')
            
            root = ET.fromstring(xml_content)
            
            # 提取不同类型的内容
            content_parts = []
            
            # 文本内容
            for text_elem in root.iter():
                if text_elem.text and text_elem.text.strip():
                    content_parts.append(text_elem.text.strip())
            
            # 链接内容
            for url_elem in root.findall('.//url'):
                if url_elem.text:
                    content_parts.append(f"链接: {url_elem.text}")
            
            # 标题内容
            for title_elem in root.findall('.//title'):
                if title_elem.text:
                    content_parts.append(f"标题: {title_elem.text}")
            
            return '\n'.join(content_parts) if content_parts else xml_content
            
        except Exception as e:
            logger.debug(f"XML解析失败: {e}")
            return xml_content
    
    async def sync_favorites_to_nexusmind(self) -> Dict[str, Any]:
        """同步微信收藏到NexusMind"""
        try:
            logger.info("开始同步微信收藏...")
            
            # 加载同步记录
            sync_record = self._load_sync_record()
            
            # 提取收藏内容
            favorites = self._extract_favorites_from_db()
            
            if not favorites:
                return {
                    'success': False,
                    'message': '未找到微信收藏数据，请确认微信已安装且有收藏内容',
                    'synced_count': 0
                }
            
            # 过滤需要同步的内容（增量同步）
            new_favorites = []
            synced_hashes = set(sync_record.get('synced_hashes', []))
            
            for favorite_data in favorites:
                parsed_content = self._parse_favorite_content(favorite_data)
                if not parsed_content:
                    continue
                
                # 生成内容哈希
                content_hash = self._generate_content_hash(
                    parsed_content['title'] + parsed_content['content']
                )
                
                # 检查是否已同步
                if content_hash not in synced_hashes:
                    parsed_content['content_hash'] = content_hash
                    new_favorites.append(parsed_content)
            
            if not new_favorites:
                return {
                    'success': True,
                    'message': '没有新的收藏内容需要同步',
                    'synced_count': 0
                }
            
            # 导入到NexusMind
            synced_count = 0
            new_hashes = []
            
            # 导入数据库和AI分析
            from database import db
            from gemini_service import analyze_content_with_gemini
            
            for favorite in new_favorites:
                try:
                    # 准备内容用于AI分析
                    full_content = f"# {favorite['title']}\n\n{favorite['content']}"
                    
                    # AI分析
                    try:
                        processed_data = await analyze_content_with_gemini(
                            full_content, 
                            original_title=favorite['title']
                        )
                    except Exception as e:
                        logger.warning(f"AI分析失败，使用默认分类: {e}")
                        processed_data = {
                            'title': favorite['title'],
                            'summary': favorite['content'][:100] + '...' if len(favorite['content']) > 100 else favorite['content'],
                            'category': '微信收藏',
                            'tags': ['微信收藏', '聊天记录']
                        }
                    
                    # 生成唯一ID
                    item_id = datetime.now().isoformat() + f"_wechat_{synced_count}"
                    
                    # 保存到数据库
                    item_data = {
                        'id': item_id,
                        'title': processed_data['title'],
                        'summary': processed_data['summary'],
                        'category': processed_data['category'],
                        'tags': processed_data['tags'],
                        'originalContent': full_content,
                        'sourceUrl': '微信收藏',
                        'createdAt': datetime.now().isoformat()
                    }
                    
                    success = db.add_knowledge_item(item_data)
                    
                    if success:
                        # 同时添加到向量数据库
                        from semantic_engine import semantic_engine
                        semantic_engine.add_document(
                            doc_id=item_id,
                            title=processed_data['title'],
                            content=full_content,
                            metadata={
                                'summary': processed_data['summary'],
                                'category': processed_data['category'],
                                'tags': processed_data['tags'],
                                'source_url': '微信收藏',
                                'created_at': item_data['createdAt']
                            }
                        )
                        
                        synced_count += 1
                        new_hashes.append(favorite['content_hash'])
                        logger.info(f"成功同步收藏: {favorite['title'][:30]}...")
                    
                except Exception as e:
                    logger.error(f"同步收藏失败: {e}")
                    continue
            
            # 更新同步记录
            sync_record['last_sync_time'] = datetime.now().isoformat()
            sync_record['synced_hashes'].extend(new_hashes)
            # 保留最近1000个哈希值，避免文件过大
            if len(sync_record['synced_hashes']) > 1000:
                sync_record['synced_hashes'] = sync_record['synced_hashes'][-1000:]
            
            self._save_sync_record(sync_record)
            
            return {
                'success': True,
                'message': f'成功同步 {synced_count} 条微信收藏到知识库',
                'synced_count': synced_count,
                'total_favorites': len(favorites)
            }
            
        except Exception as e:
            logger.error(f"同步微信收藏失败: {e}")
            return {
                'success': False,
                'message': f'同步失败: {str(e)}',
                'synced_count': 0
            }

# 全局实例 - 使用指定的微信用户路径
wechat_sync = WeChatFavoritesSync(r"C:\Users\jianqiu.chen\Documents\WeChat Files\yangyang_sunnylove")