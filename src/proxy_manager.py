"""
代理管理模块
"""
import sys
import requests
import urllib3
from typing import Optional
from .color_helper import Colors

# 关闭SSL警告
urllib3.disable_warnings()


class ProxyManager:
    """代理管理器"""
    
    def __init__(self, proxy_url: Optional[str] = None, timeout: int = 10):
        self.proxy_url = proxy_url
        self.timeout = timeout
        self.proxies = None
        
        if proxy_url:
            self.proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
    
    def test_proxy(self) -> bool:
        """
        测试代理是否可用
        
        Returns:
            代理是否可用
        """
        if not self.proxies:
            return True
        
        print(f"正在配置代理: {self.proxy_url}")
        print("正在测试代理连接...")
        
        test_urls = [
            'http://www.google.com',
            'http://www.baidu.com',
            'http://www.bing.com'
        ]
        
        for test_url in test_urls:
            try:
                response = requests.get(
                    test_url,
                    proxies=self.proxies,
                    timeout=self.timeout,
                    verify=False
                )
                if response.status_code == 200:
                    print(Colors.green(f"[+] 代理连接成功！测试URL: {test_url}"))
                    return True
            except requests.exceptions.ProxyError:
                print(Colors.red(f"[-] 代理连接失败: 无法连接到代理服务器"))
                return False
            except requests.exceptions.ConnectTimeout:
                print(Colors.red(f"[-] 代理连接超时: {test_url}"))
                continue
            except requests.exceptions.ConnectionError:
                print(Colors.red(f"[-] 代理连接错误: {test_url}"))
                continue
            except Exception:
                continue
        
        print("警告: 所有测试URL均无法访问，但代理可能仍然可用")
        print("提示: 如果目标可以访问，爆破将继续进行")
        
        # 询问是否继续
        try:
            choice = input("是否继续使用此代理? (y/n): ").strip().lower()
            if choice not in ['y', 'yes', '']:
                print("已取消操作")
                sys.exit(0)
            return True
        except KeyboardInterrupt:
            print("\n已取消操作")
            sys.exit(0)
    
    def get_proxies(self) -> Optional[dict]:
        """获取代理配置字典"""
        return self.proxies

