"""
结果管理模块
"""
import threading
from datetime import datetime
from typing import List, Optional
from .color_helper import Colors


class ResultManager:
    """结果管理器"""
    
    def __init__(self):
        self.success_results: List[dict] = []
        self.lock = threading.Lock()
    
    def add_result(self, result: dict):
        """
        添加成功结果
        
        Args:
            result: 结果字典
        """
        with self.lock:
            self.success_results.append(result)
    
    def get_results(self) -> List[dict]:
        """获取所有结果"""
        return self.success_results
    
    def get_success_count(self) -> int:
        """获取成功数量"""
        return len(self.success_results)
    
    def save_results(self, output_file: Optional[str] = None) -> bool:
        """
        保存结果到文件
        
        Args:
            output_file: 输出文件名（可选）
        
        Returns:
            是否保存成功
        """
        if not self.success_results:
            return False
        
        # 如果没有指定输出文件，使用默认文件名（保存到results目录）
        if not output_file:
            output_file = f"results/crack_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        else:
            # 如果指定了文件名但没有路径，也保存到results目录
            if '/' not in output_file and '\\' not in output_file:
                output_file = f"results/{output_file}"
        
        # 确保results目录存在
        import os
        os.makedirs('results', exist_ok=True)
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"phpMyAdmin 安全测试结果\n")
                f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"发现数量: {len(self.success_results)}\n")
                f.write(f"{'='*60}\n\n")
                
                for idx, result in enumerate(self.success_results, 1):
                    f.write(f"[{idx}] {result['time']}\n")
                    f.write(f"URL: {result['url']}\n")
                    
                    # 检查是否为未授权访问
                    if result.get('type') == '未授权访问':
                        f.write(f"类型: 未授权访问 (高危！)\n")
                        f.write(f"状态: 无需登录即可访问\n")
                        f.write(f"建议: 立即配置访问控制\n")
                    else:
                        f.write(f"用户名: {result['username']}\n")
                        f.write(f"密码: {result['password']}\n")
                        f.write(f"尝试次数: {result.get('attempts', 'N/A')}\n")
                    
                    f.write(f"{'-'*60}\n\n")
            
            print(Colors.green(f"\n[+] 成功结果已保存到: {output_file}"))
            return True
        
        except Exception as e:
            print(Colors.red(f"\n[-] 保存结果失败: {e}"))
            return False
    
    def print_summary(self, total: int, elapsed: float):
        """
        打印统计摘要
        
        Args:
            total: 总目标数
            elapsed: 耗时（秒）
        """
        success_count = self.get_success_count()
        fail_count = total - success_count
        success_rate = (success_count / total * 100) if total > 0 else 0
        avg_time = (elapsed / total) if total > 0 else 0
        
        print(f"\n{'='*60}")
        print(f"爆破完成!")
        print(f"总计: {total} 个目标")
        print(f"成功: {success_count} 个")
        print(f"失败: {fail_count} 个")
        print(f"成功率: {success_rate:.2f}%")
        print(f"总耗时: {elapsed:.2f} 秒")
        print(f"平均耗时: {avg_time:.2f} 秒/目标")
        print(f"{'='*60}")

