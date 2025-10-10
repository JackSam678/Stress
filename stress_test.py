import requests
import threading
import time
import argparse
from datetime import datetime
from collections import defaultdict
import re

class StressTester:
    def __init__(self, target, max_concurrency, total_requests, timeout=10):
        # 处理目标地址，自动补全协议和路径
        self.target = self._format_target(target)
        self.max_concurrency = max_concurrency  # 最大并发数（最大压力值）
        self.total_requests = total_requests    # 总请求数
        self.timeout = timeout                  # 超时时间（秒）
        self.results = defaultdict(int)         # 存储结果统计
        self.completed = 0                      # 已完成的请求数
        self.lock = threading.Lock()            # 线程锁
        self.start_time = None

    def _format_target(self, target):
        """格式化目标地址，确保包含协议和路径"""
        # 检查是否包含协议
        if not re.match(r'^https?://', target, re.IGNORECASE):
            # 尝试自动补全协议（先尝试http，再尝试https）
            target = f'http://{target}'
        
        # 检查是否包含路径
        if not re.search(r'//[^/]+/', target):
            # 确保路径以/结尾
            target = f'{target}/' if not target.endswith('/') else target
            
        return target

    def _send_request(self):
        """发送单个HTTP请求并记录结果"""
        try:
            start = time.time()
            response = requests.get(self.target, timeout=self.timeout, allow_redirects=True)
            duration = (time.time() - start) * 1000  # 转换为毫秒
            with self.lock:
                self.results[response.status_code] += 1
                self.results['total_time'] += duration
        except requests.exceptions.RequestException as e:
            error_type = str(type(e).__name__)
            with self.lock:
                self.results[f"error_{error_type}"] += 1
        finally:
            with self.lock:
                self.completed += 1
                # 打印进度
                if self.completed % 10 == 0 or self.completed == self.total_requests:
                    progress = (self.completed / self.total_requests) * 100
                    print(f"进度: {progress:.2f}% ({self.completed}/{self.total_requests})", end="\r")

    def run(self):
        """运行压力测试"""
        print(f"开始压力测试 - 目标: {self.target}")
        print(f"最大并发数: {self.max_concurrency}, 总请求数: {self.total_requests}")
        self.start_time = datetime.now()
        threads = []
        
        # 计算每个线程需要处理的请求数
        requests_per_thread = [self.total_requests // self.max_concurrency] * self.max_concurrency
        # 分配剩余的请求
        for i in range(self.total_requests % self.max_concurrency):
            requests_per_thread[i] += 1

        # 创建并启动线程
        for i in range(self.max_concurrency):
            thread = threading.Thread(
                target=self._thread_worker,
                args=(requests_per_thread[i],)
            )
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        self._print_results()

    def _thread_worker(self, num_requests):
        """线程工作函数，处理指定数量的请求"""
        for _ in range(num_requests):
            self._send_request()
            # 简单限流，避免瞬间请求过于集中
            time.sleep(0.001)

    def _print_results(self):
        """打印测试结果"""
        print("\n" + "="*50)
        print(f"测试结束 - 开始时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        duration = (datetime.now() - self.start_time).total_seconds()
        print(f"总耗时: {duration:.2f}秒")
        print(f"总请求数: {self.total_requests}")
        print(f"完成请求数: {self.completed}")
        
        # 计算吞吐量
        throughput = self.completed / duration if duration > 0 else 0
        print(f"吞吐量: {throughput:.2f}请求/秒")
        
        # 打印状态码统计
        print("\n状态码统计:")
        for code, count in self.results.items():
            if code.startswith("error_"):
                print(f"  {code[6:]}: {count}次")
            elif code == "total_time":
                avg_time = count / self.completed if self.completed > 0 else 0
                print(f"  平均响应时间: {avg_time:.2f}毫秒")
            else:
                print(f"  HTTP {code}: {count}次")
        print("="*50)

if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='HTTP压力测试工具，支持IP和任意网页')
    parser.add_argument('--target', default='8.211.170.143', 
                       help='目标地址，可以是IP或完整URL，例如: 8.211.170.143 或 https://example.com/path，默认: 8.211.170.143')
    parser.add_argument('--concurrency', type=int, default=5000, help='最大并发数（最大压力值），默认: 50')
    parser.add_argument('--requests', type=int, default=1000000, help='总请求数，默认: 1000')
    parser.add_argument('--timeout', type=int, default=10, help='超时时间（秒），默认: 10')
    
    args = parser.parse_args()
    
    # 创建并运行压力测试
    tester = StressTester(
        target=args.target,
        max_concurrency=args.concurrency,
        total_requests=args.requests,
        timeout=args.timeout
    )
    tester.run()
    
