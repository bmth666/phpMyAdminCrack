"""
颜色辅助模块
"""


class Colors:
    """终端颜色代码"""
    
    # 颜色代码
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    
    # 样式
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    @staticmethod
    def red(text: str) -> str:
        """红色文本（失败/错误）"""
        return f"{Colors.RED}{text}{Colors.RESET}"
    
    @staticmethod
    def green(text: str) -> str:
        """绿色文本（成功）"""
        return f"{Colors.GREEN}{text}{Colors.RESET}"
    
    @staticmethod
    def yellow(text: str) -> str:
        """黄色文本（警告）"""
        return f"{Colors.YELLOW}{text}{Colors.RESET}"
    
    @staticmethod
    def blue(text: str) -> str:
        """蓝色文本（信息）"""
        return f"{Colors.BLUE}{text}{Colors.RESET}"
    
    @staticmethod
    def cyan(text: str) -> str:
        """青色文本（进度）"""
        return f"{Colors.CYAN}{text}{Colors.RESET}"
    
    @staticmethod
    def bold(text: str) -> str:
        """粗体文本"""
        return f"{Colors.BOLD}{text}{Colors.RESET}"
    
    @staticmethod
    def success(text: str) -> str:
        """成功信息（绿色粗体）"""
        return f"{Colors.BOLD}{Colors.GREEN}{text}{Colors.RESET}"
    
    @staticmethod
    def error(text: str) -> str:
        """错误信息（红色粗体）"""
        return f"{Colors.BOLD}{Colors.RED}{text}{Colors.RESET}"
    
    @staticmethod
    def warning(text: str) -> str:
        """警告信息（黄色）"""
        return f"{Colors.YELLOW}{text}{Colors.RESET}"

