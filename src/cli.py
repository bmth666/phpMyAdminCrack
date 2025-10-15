"""
命令行接口模块
"""
import argparse
import sys


class CLI:
    """命令行接口"""
    
    def __init__(self):
        self.parser = self._create_parser()
        self.args = None
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """创建命令行参数解析器"""
        parser = argparse.ArgumentParser(
            prog='main.py',
            description='''
phpMyAdmin 弱密码爆破工具

功能说明:
  本工具用于测试phpMyAdmin的弱密码漏洞，支持单目标和批量爆破模式。
  支持多线程、代理、自定义超时等高级功能。

必需文件:
  wordlists/username.txt  - 用户名字典文件（每行一个用户名）
  wordlists/password.txt  - 密码字典文件（每行一个密码）
  wordlists/dicts.txt      - 路径字典文件（可选，用于发现phpMyAdmin路径）

注意事项:
  1. 仅用于授权测试，请勿用于非法用途
  2. 建议线程数不超过20，避免对目标造成过大压力
  3. 使用SOCKS代理需要先安装: pip install pysocks
  4. 支持的URL格式: http://example.com 或 https://example.com
            ''',
            epilog='''
示例用法:
  > 单目标爆破:
    python main.py -u http://example.com/

  > 批量爆破(单线程):
    python main.py -f urls.txt

  > 批量爆破(10线程，并发爆破10个URL):
    python main.py -f urls.txt -t 10

  > 使用SOCKS5代理:
    python main.py -f urls.txt --proxy socks5://127.0.0.1:1080

  > 使用带认证的代理:
    python main.py -f urls.txt --proxy socks5://user:pass@127.0.0.1:1080

  > 自定义超时和保存结果:
    python main.py -f urls.txt --timeout 10 -o success.txt

  > 完整配置(详细模式):
    python main.py -f urls.txt -t 10 --timeout 8 -o results.txt -v

获取帮助:
  python main.py -h        显示此帮助信息
  python main.py --help    显示详细帮助信息
            ''',
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        # 目标参数组（互斥）
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            '-u', '--url',
            metavar='URL',
            help='单个目标URL（例如: http://example.com/）'
        )
        group.add_argument(
            '-f', '--file',
            metavar='FILE',
            help='包含多个URL的文件路径（每行一个URL）'
        )
        
        # 可选参数
        parser.add_argument(
            '--proxy',
            metavar='PROXY',
            help='SOCKS代理地址（格式: socks5://127.0.0.1:1080）'
        )
        parser.add_argument(
            '-t', '--threads',
            type=int,
            default=1,
            metavar='N',
            help='线程数量，用于批量模式并发爆破多个URL（默认: 1，范围: 1-50）'
        )
        parser.add_argument(
            '-o', '--output',
            metavar='FILE',
            help='保存成功结果的文件路径（不指定则自动生成文件名）'
        )
        parser.add_argument(
            '--timeout',
            type=int,
            default=5,
            metavar='SEC',
            help='请求超时时间，单位秒（默认: 5，范围: 1-60）'
        )
        parser.add_argument(
            '-v', '--verbose',
            action='store_true',
            help='详细模式，显示每次尝试的详细信息'
        )
        
        return parser
    
    def parse_args(self):
        """解析命令行参数"""
        self.args = self.parser.parse_args()
        return self.args
    
    def print_banner(self):
        """打印工具横幅（彩色版本）"""
        from .color_helper import Colors
        
        try:
            print()
            
            # ASCII艺术字（绿色）
            ascii_art = [
                "██████╗ ███╗   ███╗ █████╗     ██████╗██████╗  █████╗  ██████╗██╗  ██╗",
                "██╔══██╗████╗ ████║██╔══██╗   ██╔════╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝",
                "██████╔╝██╔████╔██║███████║   ██║     ██████╔╝███████║██║     █████╔╝",
                "██╔═══╝ ██║╚██╔╝██║██╔══██║   ██║     ██╔══██╗██╔══██║██║     ██╔═██╗",
                "██║     ██║ ╚═╝ ██║██║  ██║   ╚██████╗██║  ██║██║  ██║╚██████╗██║  ██╗",
                "╚═╝     ╚═╝     ╚═╝╚═╝  ╚═╝    ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝"
            ]
            for line in ascii_art:
                print(f"{Colors.GREEN}{line}{Colors.RESET}")
            
            print()
            
            # 标题（黄色粗体）
            print(f"{Colors.BOLD}{Colors.YELLOW}phpMyAdmin 弱密码爆破工具{Colors.RESET}")
            print(f"{Colors.BLUE}Security Testing Tool{Colors.RESET}")
            print()
            
            # 功能特性（蓝色）
            print(f"{Colors.BLUE}[+] 支持版本: phpMyAdmin 全版本{Colors.RESET}")
            print(f"{Colors.BLUE}[+] 自动识别: 4.8.0前后版本自动适配{Colors.RESET}")
            print(f"{Colors.BLUE}[+] 多线程: 高效并发爆破{Colors.RESET}")
            print(f"{Colors.BLUE}[+] 代理支持: SOCKS5/HTTP代理{Colors.RESET}")
            print()
            
            # 警告信息（红色）
            print(f"{Colors.RED}[!] 仅用于授权的安全测试 | For Authorized Testing Only{Colors.RESET}")
            print()
            
        except (UnicodeEncodeError, Exception):
            # 编码失败或其他错误，使用简化版本
            simple_banner = f"""
{Colors.CYAN}{'='*70}{Colors.RESET}
{Colors.YELLOW}{Colors.BOLD}phpMyAdmin Weak Password Cracker{Colors.RESET}
{Colors.BLUE}Security Testing Tool{Colors.RESET}

{Colors.BLUE}[+] Support: phpMyAdmin All Versions{Colors.RESET}
{Colors.BLUE}[+] Auto Detect: 4.8.0+ / 4.8.0-{Colors.RESET}
{Colors.BLUE}[+] Multi-Threading{Colors.RESET}
{Colors.BLUE}[+] Proxy Support: SOCKS5/HTTP{Colors.RESET}

{Colors.RED}[!] For Authorized Testing Only{Colors.RESET}
{Colors.CYAN}{'='*70}{Colors.RESET}
            """
            print(simple_banner)

