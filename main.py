#!/usr/bin/env python3
"""
phpMyAdmin 弱密码爆破工具 - 主入口
面向对象版本
"""
import sys
import os
from datetime import datetime

from src.cli import CLI
from src.config import Config
from src.dict_loader import DictLoader
from src.proxy_manager import ProxyManager
from src.url_validator import URLValidator
from src.task_executor import TaskExecutor
from src.logger import init_logger, close_logger


def main():
    """主函数"""
    executor = None
    start_time = None
    
    try:
        # 创建CLI并解析参数
        cli = CLI()
        cli.print_banner()
        args = cli.parse_args()
        
        # 创建配置对象
        config = Config(
            url=args.url,
            file=args.file,
            proxy=args.proxy,
            threads=args.threads,
            timeout=args.timeout,
            output=args.output,
            verbose=args.verbose
        )
        
        # 初始化日志（始终启用，自动生成日志文件到logs目录）
        from src.color_helper import Colors
        log_file = f"logs/crack_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        init_logger(log_file)
        print(Colors.blue(f"[+] 详细日志将保存到: {log_file}"))
        
        # 测试代理（如果配置了）
        proxy_manager = None
        proxies = None
        if config.proxy:
            proxy_manager = ProxyManager(config.proxy, timeout=10)
            if not proxy_manager.test_proxy():
                print("错误: 代理连接失败，程序退出")
                sys.exit(1)
            from src.color_helper import Colors
            print(Colors.green("[+] 代理已配置并测试通过"))
            proxies = proxy_manager.get_proxies()
        
        # 加载字典
        dict_loader = DictLoader()
        dict_loader.load_all_dicts()
        
        # 创建任务执行器
        executor = TaskExecutor(config, dict_loader, proxies)
        
        # 记录开始时间
        start_time = datetime.now()
        
        # 执行任务
        if config.url:
            # 单目标模式
            executor.execute_single_mode(config.url)
        else:
            # 批量模式
            urls = URLValidator.load_urls_from_file(config.file)
            executor.execute_batch_mode(urls)
        
        # 关闭日志
        close_logger()
    
    except KeyboardInterrupt:
        # 用户中断操作
        print(f"\n\n{'='*60}")
        print(f"[!] 用户强制中断 (Ctrl+C)")
        print(f"{'='*60}")
        
        # 如果有executor和结果，保存已完成的结果
        if executor and executor.result_manager.get_success_count() > 0:
            elapsed = (datetime.now() - start_time).total_seconds() if start_time else 0
            
            print(f"\n已完成部分结果统计:")
            print(f"成功/发现: {executor.result_manager.get_success_count()} 个")
            print(f"已运行时间: {elapsed:.2f} 秒")
            
            # 保存已完成的结果
            try:
                from src.color_helper import Colors
                executor.result_manager.save_results(executor.config.output)
                print(Colors.green(f"\n[+] 已保存部分完成的结果"))
            except Exception as e:
                from src.color_helper import Colors
                print(Colors.red(f"\n[-] 保存结果失败: {e}"))
        else:
            print("\n暂无已完成的结果")
        
        print(f"{'='*60}")
        print("[!] 程序已终止")
        
        # 关闭日志
        close_logger()
        
        # 强制退出
        os._exit(0)
    
    except Exception as e:
        print(f"\n错误: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # 尝试保存已完成的结果
        if executor and executor.result_manager.get_success_count() > 0:
            try:
                print("\n[!] 尝试保存已完成的结果...")
                executor.result_manager.save_results(executor.config.output)
            except:
                pass
        
        # 关闭日志
        close_logger()
        
        sys.exit(1)


if __name__ == '__main__':
    main()

