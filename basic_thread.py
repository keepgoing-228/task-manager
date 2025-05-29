import threading
import time


def taskA(name):
    lock.acquire()
    for i in range(1, 6):
        print(f"[{name}] do {i} taskA")
        time.sleep(0.5)
        if i == 2:
            lock.release()


def taskB(name):
    lock.acquire()
    for i in range(1, 6):
        print(f"[{name}] do {i*10} taskB")
        time.sleep(0.5)
    lock.release()


def taskC(name):
    for i in range(1, 6):
        print(f"[{name}] do {i*100} taskC")
        time.sleep(0.5)


lock = threading.Lock()
t1 = threading.Thread(target=taskA, args=("threadA",))
t2 = threading.Thread(target=taskB, args=("threadB",))
t3 = threading.Thread(target=taskC, args=("threadC",))
t1.start()
t2.start()
# t3.start()

# wait for the first two threads to finish
t1.join()
t2.join()
# t3.join()
print("all tasks done")
