import threading
import time


def task(name):
    for i in range(3):
        print(f"[{name}] 做第 {i+1} 件事")
        time.sleep(1)


# 建立兩條執行緒
t1 = threading.Thread(target=task, args=("小夥伴A",))
t2 = threading.Thread(target=task, args=("小夥伴B",))

t1.start()  # 啟動第一條
t1.join()  # 等 A 做完

t2.start()  # 啟動第二條
t2.join()  # 等 B 做完
print("所有工作都做完囉！")
