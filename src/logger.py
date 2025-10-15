"""
日志记录模块
"""
import threading
import sys
import re
from datetime import datetime
from typing import Optional


class Logger:
    """日志记录器 - 始终保存详细日志到文件"""
    
    def __init__(self, log_file: Optional[str] = None):
        self.log_file = log_file
        self.lock = threading.Lock()
        self.enabled = log_file is not None
        self.verbose_mode = True  # 始终以verbose模式记录
        
        # 如果启用日志，初始化日志文件
        if self.enabled:
            try:
                # 确保logs目录存在
                import os
                os.makedirs('logs', exist_ok=True)
                
                with open(self.log_file, 'w', encoding='utf-8') as f:
                    f.write(f"phpMyAdmin 爆破工具 - 运行日志\n")
                    f.write(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"{'='*60}\n\n")
            except Exception as e:
                print(f"[警告] 无法创建日志文件: {e}")
                self.enabled = False
    
    def log(self, message: str):
        """
        记录日志
        
        Args:
            message: 日志消息
        """
        if not self.enabled:
            return
        
        try:
            with self.lock:
                # 移除ANSI颜色代码
                clean_message = self._remove_ansi_codes(message)
                
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    f.write(f"[{timestamp}] {clean_message}\n")
        except Exception:
            # 日志写入失败，静默忽略
            pass
    
    def _remove_ansi_codes(self, text: str) -> str:
        """
        移除ANSI颜色代码
        
        Args:
            text: 包含ANSI代码的文本
        
        Returns:
            纯文本
        """
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
    
    def close(self):
        """关闭日志"""
        if self.enabled:
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(f"\n{'='*60}\n")
                    f.write(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            except:
                pass


# 全局日志实例
_global_logger = None


def init_logger(log_file: Optional[str] = None):
    """
    初始化全局日志记录器
    
    Args:
        log_file: 日志文件路径
    """
    global _global_logger
    _global_logger = Logger(log_file)


def log(message: str):
    """
    记录日志到全局日志器
    
    Args:
        message: 日志消息
    """
    if _global_logger:
        _global_logger.log(message)


def close_logger():
    """关闭全局日志"""
    if _global_logger:
        _global_logger.close()

