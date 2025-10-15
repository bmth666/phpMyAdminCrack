"""
字典加载器模块
"""
import sys
from typing import List


class DictLoader:
    """字典文件加载器"""
    
    def __init__(self):
        self.usernames: List[str] = []
        self.passwords: List[str] = []
        self.paths: List[str] = []
    
    def load_file(self, filename: str, required: bool = True) -> List[str]:
        """
        加载字典文件，支持多种编码
        
        Args:
            filename: 文件名
            required: 是否必需（必需文件不存在时会退出程序）
        
        Returns:
            文件内容列表（去除空行和注释）
        """
        encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312']
        
        for encoding in encodings:
            try:
                with open(filename, encoding=encoding) as f:
                    lines = [
                        line.strip() 
                        for line in f 
                        if line.strip() and not line.strip().startswith('#')
                    ]
                    return lines
            except UnicodeDecodeError:
                continue
            except FileNotFoundError:
                if required:
                    print(f"错误: 找不到 {filename} 文件")
                    sys.exit(1)
                else:
                    return []
        
        if required:
            print(f"错误: 无法读取 {filename} 文件（编码问题）")
            sys.exit(1)
        return []
    
    def load_all_dicts(self):
        """加载所有字典文件"""
        # 加载用户名字典
        self.usernames = self.load_file("./wordlists/username.txt", required=True)
        if not self.usernames:
            print("错误: wordlists/username.txt 文件为空")
            sys.exit(1)
        
        # 加载密码字典
        self.passwords = self.load_file("./wordlists/password.txt", required=True)
        if not self.passwords:
            print("错误: wordlists/password.txt 文件为空")
            sys.exit(1)
        
        # 加载路径字典
        self.paths = self.load_file("./wordlists/dicts.txt", required=False)
        if not self.paths:
            print("警告: wordlists/dicts.txt 文件为空或不存在，将只检查根路径")
        
        print(f"已加载 {len(self.usernames)} 个用户名, "
              f"{len(self.passwords)} 个密码, "
              f"{len(self.paths)} 个路径")
    
    def get_total_combinations(self) -> int:
        """获取密码组合总数"""
        return len(self.usernames) * len(self.passwords)

