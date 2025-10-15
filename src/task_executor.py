"""
任务执行器模块
"""
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from typing import List

from .url_validator import URLValidator
from .pma_detector import PhpMyAdminDetector
from .pma_cracker import PhpMyAdminCracker
from .result_manager import ResultManager
from .color_helper import Colors
from .progress_bar import ProgressBar


class TaskExecutor:
    """任务执行器"""
    
    def __init__(self, config, dict_loader, proxies=None):
        self.config = config
        self.dict_loader = dict_loader
        self.proxies = proxies
        self.stop_flag = threading.Event()  # 停止标志
        self.progress_bar = None  # 进度条实例
        self.total_attempts_global = 0  # 全局总尝试次数
        
        # 初始化各个模块
        self.detector = PhpMyAdminDetector(
            timeout=config.timeout,
            proxies=proxies,
            verbose=config.verbose
        )
        self.cracker = PhpMyAdminCracker(
            timeout=config.timeout,
            proxies=proxies,
            verbose=config.verbose
        )
        self.result_manager = ResultManager()
    
    def crack_single_url(self, target_url: str, task_id: int = None, 
                        total: int = None) -> bool:
        """
        对单个URL进行爆破
        
        Args:
            target_url: 目标URL
            task_id: 任务ID（多线程模式）
            total: 总任务数（多线程模式）
        
        Returns:
            是否成功
        """
        use_threading = task_id is not None and total is not None
        
        # 打印开始信息
        if use_threading:
            # 多线程模式
            if self.config.verbose:
                self.detector.safe_print(
                    f"[{task_id}/{total}] 开始: {target_url}",
                    True
                )
        else:
            # 单线程模式：打印详细信息
            print(f"\n{'='*60}")
            print(f"开始爆破目标: {target_url}")
            print(f"{'='*60}")
        
        # 检查phpMyAdmin路径
        base_url = URLValidator.extract_base_url(target_url)
        pma_url = self.detector.check_path(
            base_url,
            self.dict_loader.paths,
            use_lock=use_threading,
            silent=False  # 始终显示未找到信息
        )
        
        if not pma_url:
            # check_path中已经打印了错误信息
            return False
        
        # 确保URL正确拼接
        pma_url = pma_url.rstrip('/') + '/index.php'
        
        # 获取版本和tokens
        result = self.detector.get_version_and_tokens(pma_url, use_lock=use_threading)
        if not result:
            return False
        
        version, token, session = result
        
        # 检查是否为未授权访问
        if version == 'unauthorized':
            # 发现未授权访问，直接记录结果
            # 先清除进度条，再打印（确保在新行）
            if use_threading and not self.config.verbose:
                with self.result_manager.lock:
                    print(f"\r{' '*120}\r", end='', flush=True)
            
            unauthorized_msg = Colors.success(f"[+] 未授权访问: {pma_url} (高危！)")
            self.detector.safe_print(unauthorized_msg, use_threading)
            
            # 记录到结果中
            unauthorized_result = {
                'url': pma_url,
                'username': 'N/A (未授权访问)',
                'password': 'N/A (未授权访问)',
                'attempts': 0,
                'time': __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'type': '未授权访问'
            }
            self.result_manager.add_result(unauthorized_result)
            return True
        
        # 创建进度回调函数
        def progress_callback(attempts):
            """更新全局尝试次数"""
            if self.progress_bar and use_threading:
                self.total_attempts_global += 1
        
        # 开始爆破
        crack_result = self.cracker.crack(
            pma_url,
            self.dict_loader.usernames,
            self.dict_loader.passwords,
            token,
            session,
            use_lock=use_threading,
            progress_callback=progress_callback if use_threading else None,
            version=version  # 传递版本信息
        )
        
        if crack_result:
            self.result_manager.add_result(crack_result)
            return True
        
        return False
    
    def execute_single_mode(self, url: str):
        """
        执行单目标模式
        
        Args:
            url: 目标URL
        """
        print(f"\n{'='*60}")
        print(f"开始单目标爆破模式")
        print(f"目标: {url}")
        print(f"超时设置: {self.config.timeout} 秒")
        if self.config.proxy:
            print(f"使用代理: {self.config.proxy}")
        print(f"预计密码组合: {self.dict_loader.get_total_combinations()}")
        print(f"{'='*60}")
        
        start_time = datetime.now()
        result = self.crack_single_url(url)
        elapsed = (datetime.now() - start_time).total_seconds()
        
        print(f"\n{'='*60}")
        print(f"单目标爆破完成!")
        print(f"结果: {'成功' if result else '失败'}")
        print(f"耗时: {elapsed:.2f} 秒")
        print(f"{'='*60}")
        
        self.result_manager.save_results(self.config.output)
    
    def execute_batch_mode(self, urls: List[str]):
        """
        执行批量模式
        
        Args:
            urls: URL列表
        """
        print(f"\n{'='*60}")
        print(f"开始批量爆破模式")
        print(f"目标数量: {len(urls)} 个有效URL")
        print(f"配置线程数: {self.config.threads} 个线程")
        print(f"超时设置: {self.config.timeout} 秒")
        if self.config.proxy:
            print(f"使用代理: {self.config.proxy}")
        if self.config.verbose:
            print(f"详细模式: 开启")
        print(f"预计密码组合: {self.dict_loader.get_total_combinations()}")
        print(f"\n提示: 按 Ctrl+C 可随时中断并保存已完成的结果")
        print(f"{'='*60}\n")
        
        start_time = datetime.now()
        success_count = 0
        fail_count = 0
        
        try:
            if self.config.threads == 1:
                # 单线程模式
                for idx, url in enumerate(urls, 1):
                    print(f"\n进度: [{idx}/{len(urls)}]")
                    result = self.crack_single_url(url)
                    if result:
                        success_count += 1
                    else:
                        fail_count += 1
            else:
                # 多线程模式
                thread_executor = ThreadPoolExecutor(max_workers=self.config.threads)
                
                # 创建进度条（非verbose模式）
                if not self.config.verbose:
                    total_combinations = self.dict_loader.get_total_combinations()
                    total_attempts = len(urls) * total_combinations
                    self.progress_bar = ProgressBar(len(urls), prefix="Request Progress", total_attempts=total_attempts)
                else:
                    self.progress_bar = None
                
                try:
                    # 提交所有任务
                    future_to_url = {}
                    for idx, url in enumerate(urls, 1):
                        future = thread_executor.submit(self.crack_single_url, url, idx, len(urls))
                        future_to_url[future] = url
                    
                    # 收集结果（添加超时以支持Ctrl+C）
                    completed = 0
                    while future_to_url:
                        # 使用短超时周期性检查，支持Ctrl+C中断
                        done_futures = []
                        has_update = False
                        
                        for future in list(future_to_url.keys()):
                            try:
                                # 设置短超时（0.1秒），更快响应Ctrl+C
                                result = future.result(timeout=0.1)
                                completed += 1
                                has_update = True
                                
                                if result:
                                    success_count += 1
                                else:
                                    fail_count += 1
                                
                                done_futures.append(future)
                            
                            except TimeoutError:
                                # 超时，继续等待
                                continue
                            except Exception as e:
                                with self.result_manager.lock:
                                    # 先清除进度条，再打印错误
                                    if self.progress_bar:
                                        self.progress_bar.clear()
                                    print(f"[错误] {future_to_url[future]} 线程执行异常: {str(e)}")
                                fail_count += 1
                                completed += 1
                                has_update = True
                                done_futures.append(future)
                        
                        # 更新进度条（实时刷新，显示当前尝试进度）
                        if self.progress_bar:
                            with self.result_manager.lock:
                                self.progress_bar.update(
                                    completed, 
                                    success_count, 
                                    fail_count,
                                    current_attempts=self.total_attempts_global
                                )
                        
                        # 移除已完成的future
                        for future in done_futures:
                            del future_to_url[future]
                
                except KeyboardInterrupt:
                    # 收到中断信号，立即停止
                    if self.progress_bar:
                        self.progress_bar.clear()
                    print(f"\n\n[!] 正在停止...")
                    
                    # 取消所有未完成的任务
                    cancelled = 0
                    for future in future_to_url.keys():
                        if future.cancel():
                            cancelled += 1
                    
                    # 立即关闭线程池（不等待）
                    thread_executor.shutdown(wait=False)
                    
                    print(f"[+] 已取消 {cancelled} 个未完成任务")
                    raise  # 重新抛出，让main处理
                
                finally:
                    # 确保线程池被关闭
                    try:
                        thread_executor.shutdown(wait=False)
                    except:
                        pass
                    
                    # 完成进度条
                    if self.progress_bar:
                        self.progress_bar.finish()
        
        except KeyboardInterrupt:
            # 批量模式中的中断处理（外层捕获）
            raise  # 直接抛出，让main函数处理
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        # 显示统计结果
        self.result_manager.print_summary(len(urls), elapsed)
        
        # 保存结果
        self.result_manager.save_results(self.config.output)

