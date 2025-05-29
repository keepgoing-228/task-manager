import time

print("B start")
for i in range(5):
    print(f"B do {(i+1)*10} tasks")
    time.sleep(0.5)
print("B end")
