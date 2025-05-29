import threading
import time


def taskA(name):
    for i in range(3):
        print(f"[{name}] do {i+1} taskA")
        time.sleep(0.5)


def taskB(name):
    for i in range(3):
        print(f"[{name}] do {i+1} taskB")
        time.sleep(0.5)


def taskC(name):
    for i in range(3):
        print(f"[{name}] do {i+1} taskC")
        time.sleep(0.5)


t1 = threading.Thread(target=taskA, args=("threadA",))
t2 = threading.Thread(target=taskB, args=("threadB",))
t3 = threading.Thread(target=taskC, args=("threadC",))
t1.start()
t2.start()

# wait for the first two threads to finish
t1.join()
t2.join()

# start the third thread after the first two threads finish
t3.start()
t3.join()

print("all tasks done")
