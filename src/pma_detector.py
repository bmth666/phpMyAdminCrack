"""
phpMyAdmin检测模块
"""
import re
import requests
import urllib3
from typing import Optional, Tuple
import threading
from .color_helper import Colors

# 关闭SSL警告
urllib3.disable_warnings()


class PhpMyAdminDetector:
    """phpMyAdmin路径和版本检测器"""
    
    def __init__(self, timeout: int = 5, proxies: Optional[dict] = None, verbose: bool = False):
        self.timeout = timeout
        self.proxies = proxies
        self.verbose = verbose
        self.print_lock = threading.Lock()
    
    def safe_print(self, message: str, use_lock: bool = False, log_only: bool = False):
        """
        线程安全的打印函数
        
        Args:
            message: 消息内容
            use_lock: 是否使用线程锁
            log_only: 是否只记录日志不打印（用于非verbose模式但要记录日志的情况）
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
    
    def is_phpmyadmin(self, response_text: str) -> bool:
        """
        判断是否为phpMyAdmin页面(通过title标签判断)
        
        Args:
            response_text: 响应文本
        
        Returns:
            是否为phpMyAdmin
        """
        # 从title标签中检查是否包含phpMyAdmin
        title_match = re.search(r'<title>([^<]+)</title>', response_text, re.IGNORECASE)
        if title_match:
            title_text = title_match.group(1)
            # 不区分大小写检查phpMyAdmin
            if 'phpmyadmin' in title_text.lower():
                return True
        
        return False
    
    def check_path(self, base_url: str, paths: list, use_lock: bool = False, silent: bool = False) -> Optional[str]:
        """
        检查phpMyAdmin路径
        
        Args:
            base_url: 基础URL
            paths: 路径字典列表
            use_lock: 是否使用线程锁
            silent: 是否静默模式（不打印发现信息）
        
        Returns:
            找到的phpMyAdmin URL或None
        """
        if not base_url:
            return None
        
        try:
            # 设置浏览器headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.6828.70 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive'
            }
            
            # 先检查根路径
            test_url = base_url.rstrip('/') + '/'
            response = requests.get(
                test_url,
                headers=headers,
                timeout=self.timeout,
                verify=False,
                proxies=self.proxies,
                allow_redirects=False
            )
            
            if response.status_code == 200:
                # 使用is_phpmyadmin方法检查title
                if self.is_phpmyadmin(response.text):
                    if not silent:
                        # 多线程模式下先清除进度条
                        if use_lock:
                            print(f"\r{' '*120}\r", end='', flush=True)
                        self.safe_print(Colors.blue(f"[+] 发现: {test_url}"), use_lock)
                    return test_url
            
            # 遍历字典路径
            for path in paths:
                clean_path = path.strip().strip('/')
                if not clean_path:
                    continue
                
                url_to_test = test_url.rstrip('/') + '/' + clean_path + '/'
                
                try:
                    response = requests.get(
                        url_to_test,
                        headers=headers,
                        timeout=self.timeout,
                        verify=False,
                        proxies=self.proxies
                    )
                    
                    if response.status_code == 200:
                        # 使用is_phpmyadmin方法检查title
                        if self.is_phpmyadmin(response.text):
                            if not silent:
                                # 多线程模式下先清除进度条
                                if use_lock:
                                    print(f"\r{' '*120}\r", end='', flush=True)
                                self.safe_print(Colors.blue(f"[+] 发现: {url_to_test}"), use_lock)
                            return url_to_test.rstrip('/') + '/'
                except requests.RequestException:
                    continue
            
            # 未找到phpMyAdmin - 始终显示（红色）
            if use_lock:
                print(f"\r{' '*120}\r", end='', flush=True)
            self.safe_print(Colors.red(f"[-] 未找到phpMyAdmin: {test_url.rstrip('/')}"), use_lock)
            return None
        
        except requests.RequestException as e:
            if use_lock:
                print(f"\r{' '*120}\r", end='', flush=True)
            self.safe_print(Colors.red(f"[-] 错误: {base_url} - 请求错误: {e}"), use_lock)
            return None
        except Exception as e:
            if use_lock:
                print(f"\r{' '*120}\r", end='', flush=True)
            self.safe_print(Colors.red(f"[-] 错误: {base_url} - 未知错误: {e}"), use_lock)
            return None
    
    @staticmethod
    def compare_version(version: str, target: str) -> int:
        """
        比较版本号
        
        Args:
            version: 当前版本
            target: 目标版本
        
        Returns:
            1: version > target
            0: version == target
            -1: version < target
        """
        try:
            v_parts = [int(x) for x in version.split('.')]
            t_parts = [int(x) for x in target.split('.')]
            
            # 补齐长度
            max_len = max(len(v_parts), len(t_parts))
            v_parts += [0] * (max_len - len(v_parts))
            t_parts += [0] * (max_len - len(t_parts))
            
            for v, t in zip(v_parts, t_parts):
                if v > t:
                    return 1
                elif v < t:
                    return -1
            return 0
        except:
            return 0
    
    def check_unauthorized_access(self, response_text: str) -> bool:
        """
        检查是否存在未授权访问
        
        Args:
            response_text: 响应文本
        
        Returns:
            True: 存在未授权访问（无需登录）
            False: 需要登录
        """
        # 检测关键字段，这些字段只在已登录状态下出现
        unauthorized_keywords = [
            'General settings',
            'Web server',
            'Appearance settings',
            'Database server',
            'Version information',
            'Server type',
            'PHP version',
            'Server:',
            'Server charset'
        ]
        
        # 同时检查是否不存在登录表单
        login_indicators = [
            'pma_username',
            'pma_password',
            'Log in'
        ]
        
        # 如果存在多个未授权访问的关键词，并且不存在登录表单
        keyword_count = sum(1 for keyword in unauthorized_keywords if keyword in response_text)
        has_login_form = any(indicator in response_text for indicator in login_indicators)
        
        # 如果有3个以上的关键词且没有登录表单，则判断为未授权访问
        return keyword_count >= 3 and not has_login_form
    
    def get_version_and_tokens(self, pma_url: str, use_lock: bool = False) -> Optional[Tuple[str, re.Match, Optional[re.Match]]]:
        """
        获取phpMyAdmin版本、token和session
        
        Args:
            pma_url: phpMyAdmin URL
            use_lock: 是否使用线程锁
        
        Returns:
            (version, token, session) 或 None
            注意：对于4.8.0之前的版本，session为None
            如果检测到未授权访问，返回 ('unauthorized', None, None)
        """
        try:
            # 设置浏览器headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.6828.70 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            response = requests.get(
                pma_url,
                headers=headers,
                timeout=self.timeout,
                verify=False,
                proxies=self.proxies
            )
            
            # 检查响应状态
            if response.status_code != 200:
                # 在多线程模式下，先清除进度条
                if use_lock:
                    print(f"\r{' '*120}\r", end='', flush=True)
                self.safe_print(Colors.red(f"[-] 失败: {pma_url} - 服务器返回状态码 {response.status_code}"), use_lock)
                return None
            
            # 检查响应内容
            if not response.text or len(response.text) < 100:
                # 在多线程模式下，先清除进度条
                if use_lock:
                    print(f"\r{' '*120}\r", end='', flush=True)
                self.safe_print(Colors.red(f"[-] 失败: {pma_url} - 响应内容异常"), use_lock)
                return None
            
            # 检查是否存在未授权访问
            if self.check_unauthorized_access(response.text):
                # 打印检测结果（只在verbose时显示）
                if self.verbose:
                    self.safe_print(f"[!] {pma_url} - 未授权访问！", use_lock)
                return ('unauthorized', None, None)
            
            # 获取token
            token = re.search(r'(?<=name="token" value=")[^"]+', response.text)
            if not token:
                # 在多线程模式下，先清除进度条
                if use_lock:
                    print(f"\r{' '*120}\r", end='', flush=True)
                self.safe_print(Colors.red(f"[-] 失败: {pma_url} - 无法获取token"), use_lock)
                return None
            
            # 获取版本信息
            version_match = re.search(r'\?v=([\d\.]+)', response.text)
            version = None
            
            if not version_match:
                # 方法1失败，尝试从documentation页面获取版本
                try:
                    # 构建documentation URL
                    base_path = pma_url.rsplit('/', 1)[0]  # 移除index.php
                    doc_url = f"{base_path}/doc/html/index.html"
                    
                    doc_response = requests.get(
                        doc_url,
                        headers=headers,
                        timeout=self.timeout,
                        verify=False,
                        proxies=self.proxies
                    )
                    
                    if doc_response.status_code == 200:
                        # 从 <a href="#">phpMyAdmin 4.1.8 documentation</a> 提取版本
                        doc_version_match = re.search(r'phpMyAdmin\s+([\d\.]+)\s+documentation', doc_response.text, re.IGNORECASE)
                        if doc_version_match:
                            version = doc_version_match.group(1)
                            # 显示从documentation获取的版本
                            self.safe_print(
                                Colors.blue(f"[+] {pma_url} - 版本: {version} (从documentation获取)"), 
                                use_lock,
                                log_only=(not self.verbose and use_lock)
                            )
                except:
                    pass
                
                # 如果documentation也失败，通过set_session判断
                if not version:
                    if self.verbose or not use_lock:
                        self.safe_print(Colors.yellow(f"[-] 警告: {pma_url} - 版本获取失败，通过set_session判断"), use_lock)
                
                session = re.search(r'(?<=name="set_session" value=")[^"]+', response.text)
                if not session:
                    # 不存在set_session，按4.8.0之前版本处理
                    self.safe_print(
                        Colors.blue(f"[+] {pma_url} - 未知版本，按旧版本(<4.8.0)处理"), 
                        use_lock,
                        log_only=(not self.verbose and use_lock)
                    )
                    return ('unknown-legacy', token, None)
                else:
                    # 存在set_session，按4.8.0之后版本处理
                    self.safe_print(
                        Colors.blue(f"[+] {pma_url} - 未知版本，按新版本(>=4.8.0)处理"), 
                        use_lock,
                        log_only=(not self.verbose and use_lock)
                    )
                    return ('unknown-new', token, session)
            else:
                version = version_match.group(1)
                # 显示版本信息
                self.safe_print(
                    Colors.blue(f"[+] {pma_url} - 版本: {version}"), 
                    use_lock,
                    log_only=(not self.verbose and use_lock)
                )
            
            # 判断版本，4.8.0之前不需要set_session参数
            if version and self.compare_version(version, "4.8.0") < 0:
                return (version, token, None)
            else:
                # 4.8.0及之后需要session
                session = re.search(r'(?<=name="set_session" value=")[^"]+', response.text)
                if not session:
                    # 在多线程模式下，先清除进度条
                    if use_lock:
                        print(f"\r{' '*120}\r", end='', flush=True)
                    self.safe_print(Colors.red(f"[-] 失败: {pma_url} - 无法获取set_session"), use_lock)
                    return None
                return (version, token, session)
        
        except requests.RequestException as e:
            # 在多线程模式下，先清除进度条
            if use_lock:
                print(f"\r{' '*120}\r", end='', flush=True)
            self.safe_print(Colors.red(f"[-] 错误: {pma_url} - 网络请求错误: {str(e)}"), use_lock)
            return None
        except Exception as e:
            # 在多线程模式下，先清除进度条
            if use_lock:
                print(f"\r{' '*120}\r", end='', flush=True)
            self.safe_print(Colors.red(f"[-] 错误: {pma_url} - 未知错误: {str(e)}"), use_lock)
            return None

