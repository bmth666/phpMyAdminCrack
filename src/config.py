"""
配置管理模块
"""
import sys
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """配置类，管理所有运行参数"""
    
    # 目标参数
    url: Optional[str] = None
    file: Optional[str] = None
    
    # 代理配置
    proxy: Optional[str] = None
    
    # 性能参数
    threads: int = 1
    timeout: int = 5
    
    # 输出参数
    output: Optional[str] = None
    verbose: bool = False
    
    def __post_init__(self):
        """参数验证"""
        self._validate_threads()
        self._validate_timeout()
        self._validate_target()
    
    def _validate_threads(self):
        """验证线程数"""
        if self.threads < 1:
            print("错误: 线程数必须大于0")
            sys.exit(1)
        if self.threads > 50:
            print("警告: 线程数过大，已自动限制为50")
            self.threads = 50
    
    def _validate_timeout(self):
        """验证超时时间"""
        if self.timeout < 1:
            print("错误: 超时时间必须大于0秒")
            sys.exit(1)
        if self.timeout > 60:
            print("警告: 超时时间过长，已自动限制为60秒")
            self.timeout = 60
    
    def _validate_target(self):
        """验证目标参数"""
        if not self.url and not self.file:
            print("错误: 必须指定URL(-u)或文件(-f)参数")
            sys.exit(1)
    
    def get_proxies(self) -> Optional[dict]:
        """获取代理配置"""
        if self.proxy:
            return {
                'http': self.proxy,
                'https': self.proxy
            }
        return None
    
    def print_config(self):
        """打印配置信息"""
        print(f"{'='*60}")
        if self.url:
            print(f"运行模式: 单目标爆破")
            print(f"目标URL: {self.url}")
        else:
            print(f"运行模式: 批量爆破")
            print(f"URL文件: {self.file}")
            print(f"线程数: {self.threads}")
        
        print(f"超时设置: {self.timeout} 秒")
        
        if self.proxy:
            print(f"使用代理: {self.proxy}")
        
        if self.verbose:
            print(f"详细模式: 开启")
        
        if self.output:
            print(f"输出文件: {self.output}")
        
        print(f"{'='*60}")

