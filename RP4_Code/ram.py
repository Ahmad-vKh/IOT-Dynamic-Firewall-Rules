import psutil
import time
import multiprocessing
import random


def get_average_ram_utilization(duration, result_queue):
    interval = 1
    start_time = time.time()
    utilization_values = []
    while time.time() - start_time < duration:
        ram_usage = psutil.virtual_memory().percent
        utilization_values.append(ram_usage)
        time.sleep(interval)
    avg_utilization = sum(utilization_values) / len(utilization_values)
    result_queue.put(avg_utilization)
    print(
        f"[+] Allocated {avg_utilization:.2f}% of available RAM for {duration} seconds..."
    )
    print("#" * 5)
    # print('ysfc',avg_utilization)


def consume_ram(target_percentage, duration):
    assert 0 <= target_percentage <= 100, "Utilization must be between 0 and 100"
    total_memory = psutil.virtual_memory().total
    current_usage = psutil.virtual_memory().percent
    available_memory = total_memory * ((100 - current_usage) / 100)
    target_memory = available_memory * (target_percentage / 100)
    # target_memory = total_memory * (target_percentage / 100)

    allocated_memory = bytearray(int(target_memory))

    start_time = time.time()
    while time.time() - start_time < duration:
        time.sleep(0.5)
    del allocated_memory
    print("RAM utilization released.")


def main(duration, result_queue):

    if random.random() < 0.5:
        target_ram = random.randint(5, 10)  # Below 50%
    else:
        target_ram = random.randint(51, 70)  # Above 50%

    process_1 = multiprocessing.Process(target=consume_ram, args=(target_ram, duration))
    process_2 = multiprocessing.Process(
        target=get_average_ram_utilization, args=(duration, result_queue)
    )
    process_1.start()
    process_2.start()
    process_1.join()
    process_2.join()


if __name__ == "__main__":
    result_queue = multiprocessing.Queue()
    main(10, result_queue)
    ram_usage = result_queue.get()
    print(f"Average RAM utilization: {ram_usage:.2f}%")
