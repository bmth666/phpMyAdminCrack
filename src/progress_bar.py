"""
进度条模块
"""
import time
from datetime import datetime
from .color_helper import Colors


class ProgressBar:
    """进度条显示类"""
    
    def __init__(self, total: int, prefix: str = "进度", total_attempts: int = 0):
        self.total = total
        self.prefix = prefix
        self.current = 0
        self.success = 0
        self.failed = 0
        self.start_time = time.time()
        self.bar_length = 20  # 进度条长度
        self.total_attempts = total_attempts  # 总尝试次数
        self.current_attempts = 0  # 当前已尝试次数
        self.current_url = ""  # 当前正在处理的URL
    
    def update(self, completed: int, success: int, failed: int, current_url: str = "", current_attempts: int = 0):
        """
        更新进度
        
        Args:
            completed: 已完成URL数量
            success: 成功数量
            failed: 失败数量
            current_url: 当前处理的URL
            current_attempts: 当前已尝试次数（累计）
        """
        self.current = completed
        self.success = success
        self.failed = failed
        self.current_url = current_url
        if current_attempts > 0:
            self.current_attempts = current_attempts
        
        # 计算百分比（基于URL数量，更准确）
        percent = (self.current / self.total * 100) if self.total > 0 else 0
        
        # 计算进度条填充（基于URL数量）
        filled_length = int(self.bar_length * self.current / self.total) if self.total > 0 else 0
        
        # 创建进度条
        bar = '█' * filled_length + '░' * (self.bar_length - filled_length)
        
        # 计算速度和剩余时间（基于URL数量）
        elapsed = time.time() - self.start_time
        
        # 使用URL数量计算速度和剩余时间
        speed = self.current / elapsed if elapsed > 0 else 0
        
        # 计算剩余时间
        if speed > 0:
            remaining = (self.total - self.current) / speed
            eta = self._format_time(remaining)
        else:
            eta = "N/A"
        
        # 计算尝试速度（仅用于显示）
        attempt_speed = self.current_attempts / elapsed if elapsed > 0 and self.current_attempts > 0 else 0
        
        # 格式化已用时间
        elapsed_str = self._format_time(elapsed)
        
        # 构建进度条字符串（主进度基于URL数量）
        progress_str = (
            f"\r{self.prefix}: {percent:>5.1f}%|{bar}| "
            f"URL:{self.current}/{self.total} "
            f"[{elapsed_str}<{eta}, {speed:.2f}url/s] "
            f"成功:{Colors.GREEN}{self.success}{Colors.RESET} "
            f"失败:{Colors.RED}{self.failed}{Colors.RESET}"
        )
        
        # 如果有尝试次数统计，显示为辅助信息
        if self.total_attempts > 0 and self.current_attempts > 0:
            progress_str += f" | 尝试:{self.current_attempts} ({attempt_speed:.1f}/s)"
        
        print(progress_str, end='', flush=True)
    
    def _format_time(self, seconds: float) -> str:
        """
        格式化时间
        
        Args:
            seconds: 秒数
        
        Returns:
            格式化的时间字符串 (MM:SS)
        """
        if seconds < 0:
            return "00:00"
        
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        
        if minutes >= 60:
            hours = minutes // 60
            minutes = minutes % 60
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"
    
    def finish(self):
        """完成进度条"""
        print()  # 换行
    
    def clear(self):
        """清除进度条"""
        print(f"\r{' '*120}\r", end='', flush=True)

