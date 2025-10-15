"""
URL验证和处理模块
"""
from urllib.parse import urlparse, urlunparse
from typing import Optional, List
import sys


class URLValidator:
    """URL验证和处理类"""
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """
        验证URL格式
        
        Args:
            url: 待验证的URL
        
        Returns:
            是否有效
        """
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False
            if parsed.scheme not in ['http', 'https']:
                return False
            return True
        except:
            return False
    
    @staticmethod
    def extract_base_url(url: str) -> Optional[str]:
        """
        提取基础URL（去除路径、参数等）
        
        Args:
            url: 原始URL
        
        Returns:
            基础URL或None
        """
        try:
            if not URLValidator.validate_url(url):
                print(f"URL格式错误: {url}")
                return None
            
            parsed = urlparse(url)
            clean_url = urlunparse((
                parsed.scheme,      # 协议
                parsed.netloc,      # 域名:端口
                '',                 # 路径
                '',                 # 参数
                '',                 # 查询
                ''                  # 片段
            ))
            return clean_url
        except Exception as e:
            print(f"URL解析错误: {e}")
            return None
    
    @staticmethod
    def load_urls_from_file(filename: str) -> List[str]:
        """
        从文件加载URL列表
        
        Args:
            filename: 文件名
        
        Returns:
            有效的URL列表
        """
        encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312']
        urls = []
        
        for encoding in encodings:
            try:
                with open(filename, encoding=encoding) as f:
                    urls = [
                        line.strip() 
                        for line in f 
                        if line.strip() and not line.strip().startswith('#')
                    ]
                break
            except UnicodeDecodeError:
                continue
            except FileNotFoundError:
                print(f"错误: 找不到文件 {filename}")
                sys.exit(1)
        
        # 验证URL格式
        valid_urls = []
        for url in urls:
            if URLValidator.validate_url(url):
                valid_urls.append(url)
            else:
                print(f"警告: 跳过无效URL - {url}")
        
        if not valid_urls:
            print("错误: 没有有效的URL")
            sys.exit(1)
        
        if len(valid_urls) < len(urls):
            print(f"警告: 已过滤 {len(urls) - len(valid_urls)} 个无效URL\n")
        
        return valid_urls

