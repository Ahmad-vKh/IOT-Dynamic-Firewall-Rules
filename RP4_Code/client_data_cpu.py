import random
import time
import psutil
import hashlib
import multiprocessing


def S_cpu_utilization(d_utilization, t):
    assert 0 <= d_utilization <= 100, "Utilization must be between 0 and 100"
    period = 1
    work_time = period * (d_utilization / 100)
    sleep_time = period - work_time
    sentence = "This is a test sentence to hash"
    end_time = time.time() + t
    while time.time() < end_time:
        start = time.time()
        while time.time() - start < work_time:
            hashlib.sha256(sentence.encode()).hexdigest()
        if sleep_time > 0:
            time.sleep(sleep_time)


def M_cpu_utilization(d_utilization, t):
    num_cores = multiprocessing.cpu_count()
    processes = []
    for i in range(num_cores):
        p = multiprocessing.Process(target=S_cpu_utilization, args=(d_utilization, t))
        p.start()
        processes.append(p)
    for p in processes:
        p.join()


def get_cpu_percentage(t, return_queue):
    cpu_utilization = psutil.cpu_percent(interval=t)
    return_queue.put(cpu_utilization)


def random_data_generation(t, data_queue):
    s_time = time.time()
    binary_data = None
    while time.time() - s_time < t:
        x = bin(random.getrandbits(16))
        binary_data = x.replace("0b", "").zfill(16)
        time.sleep(0.5)
    cpu_usage = psutil.cpu_percent(interval=0.1)

    data_queue.put((binary_data))  # Return binary data


def idle_activity():
    return random.randint(10, 29)


def moderate_activity():
    return random.randint(30, 70)


def critical_activity():
    return random.randint(71, 95)


def main(t, cpu_queue, data_queue):
    mode = random.choice(["idle", "moderate", "critical"])

    if mode == "idle":
        cpu = idle_activity()
    elif mode == "moderate":
        cpu = moderate_activity()
    else:
        cpu = critical_activity()

    print(f"[+] Simulating {mode.upper()} activity with target CPU: {cpu}%")

    cpu_monitor_process = multiprocessing.Process(
        target=get_cpu_percentage, args=(t, cpu_queue)
    )
    data_process = multiprocessing.Process(
        target=random_data_generation, args=(t, data_queue)
    )
    cpu_monitor_process.start()
    data_process.start()
    M_cpu_utilization(d_utilization=cpu, t=t)
    cpu_monitor_process.join()
    data_process.join()


if __name__ == "__main__":
    cpu_queue = multiprocessing.Queue()
    data_queue = multiprocessing.Queue()
    main(10, cpu_queue, data_queue)
    cpu_usage = cpu_queue.get()
    binary_data = data_queue.get()
    print(f"CPU Usage: {cpu_usage}%")

    print(f"Binary Data: {binary_data}")
