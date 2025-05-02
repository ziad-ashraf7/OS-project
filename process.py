import random
import numpy as np


class Process:
    def __init__(self, pid, arrival_time, burst_time, priority=None):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.priority = priority
        self.start_time = None
        self.completion_time = None
        self.waiting_time = 0
        self.turnaround_time = 0
        self.response_time = None

    def __str__(self):
        return f"Process {self.pid}: AT={self.arrival_time}, BT={self.burst_time}, Priority={self.priority}"

    def calculate_metrics(self):
        if self.completion_time is not None:
            self.turnaround_time = self.completion_time - self.arrival_time
            self.waiting_time = self.turnaround_time - self.burst_time
            if self.start_time is not None:
                self.response_time = self.start_time - self.arrival_time

    @staticmethod
    def generate_random_processes(num_processes):
        processes = []
        for i in range(1, num_processes + 1):  # Start from 1 to match PID
            arrival_time = random.randint(0, 10)
            burst_time = random.randint(1, 10)
            priority = random.randint(1, 5)
            process = Process(i, arrival_time, burst_time, priority)
            processes.append(process)
        return sorted(processes, key=lambda x: x.arrival_time)  # Sort by arrival time

    @staticmethod
    def generate_processes_from_file(input_file):
        with open(input_file) as f:
            num_processes = int(f.readline().strip())
            arrival_mean, arrival_std = map(float, f.readline().strip().split())
            burst_mean, burst_std = map(float, f.readline().strip().split())
            priority_lambda = float(f.readline().strip())

        processes = []
        for i in range(1, num_processes + 1):
            arrival = max(0, round(np.random.normal(arrival_mean, arrival_std), 1))
            burst = max(0.1, round(np.random.normal(burst_mean, burst_std), 1))
            priority = max(1, np.random.poisson(priority_lambda))
            processes.append(Process(i, arrival, burst, priority))

        return processes

    @staticmethod
    def write_to_file(processes, output_file):
        with open(output_file, 'w') as f:
            f.write(f"{len(processes)}\n")
            for p in processes:
                f.write(f"{p.pid} {p.arrival_time} {p.burst_time} {p.priority}\n")