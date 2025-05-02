from process import Process
from typing import List, Tuple
import heapq


class SchedulingAlgorithms:
    @staticmethod
    def fcfs(processes: List[Process]) -> Tuple[List[Process], List[Tuple[int, int, int]]]:
        processes = sorted(processes, key=lambda x: x.arrival_time)
        current_time = 0
        gantt_chart = []

        for process in processes:
            if current_time < process.arrival_time:
                current_time = process.arrival_time
            process.start_time = current_time
            process.completion_time = current_time + process.burst_time
            process.calculate_metrics()
            gantt_chart.append((process.pid, current_time, process.completion_time))
            current_time = process.completion_time

        return processes, gantt_chart

    @staticmethod
    def sjf(processes: List[Process]) -> Tuple[List[Process], List[Tuple[int, int, int]]]:
        processes = sorted(processes, key=lambda x: x.arrival_time)
        current_time = 0
        gantt_chart = []
        ready_queue = []
        i = 0

        while i < len(processes) or ready_queue:
            while i < len(processes) and processes[i].arrival_time <= current_time:
                heapq.heappush(ready_queue, (processes[i].burst_time, i))
                i += 1

            if ready_queue:
                burst, idx = heapq.heappop(ready_queue)
                process = processes[idx]
                process.start_time = current_time
                process.completion_time = current_time + process.burst_time
                process.calculate_metrics()
                gantt_chart.append((process.pid, current_time, process.completion_time))
                current_time = process.completion_time
            else:
                current_time = processes[i].arrival_time

        return processes, gantt_chart

    @staticmethod
    def priority(processes: List[Process]) -> Tuple[List[Process], List[Tuple[int, int, int]]]:
        processes = sorted(processes, key=lambda x: x.arrival_time)
        current_time = 0
        gantt_chart = []
        ready_queue = []
        i = 0

        while i < len(processes) or ready_queue:
            while i < len(processes) and processes[i].arrival_time <= current_time:
                heapq.heappush(ready_queue, (processes[i].priority, i))
                i += 1

            if ready_queue:
                priority, idx = heapq.heappop(ready_queue)
                process = processes[idx]
                process.start_time = current_time
                process.completion_time = current_time + process.burst_time
                process.calculate_metrics()
                gantt_chart.append((process.pid, current_time, process.completion_time))
                current_time = process.completion_time
            else:
                current_time = processes[i].arrival_time

        return processes, gantt_chart

    @staticmethod
    def round_robin(processes: List[Process], time_quantum: int) -> Tuple[List[Process], List[Tuple[int, int, int]]]:
        # Initialize remaining_time and reset process states
        for p in processes:
            p.remaining_time = p.burst_time
            p.start_time = None
            p.completion_time = None

        processes = sorted(processes, key=lambda x: x.arrival_time)
        current_time = 0
        gantt_chart = []
        ready_queue = []
        i = 0  # Tracks the next process to arrive

        while i < len(processes) or ready_queue:
            # Add arriving processes to the ready queue
            while i < len(processes) and processes[i].arrival_time <= current_time:
                ready_queue.append(i)
                i += 1

            if ready_queue:
                idx = ready_queue.pop(0)
                process = processes[idx]

                # Set start_time if this is the first execution
                if process.start_time is None:
                    process.start_time = current_time

                # Determine execution time (min of quantum or remaining time)
                execution_time = min(time_quantum, process.remaining_time)
                gantt_chart.append((process.pid, current_time, current_time + execution_time))
                current_time += execution_time
                process.remaining_time -= execution_time

                # Re-add to queue if remaining_time > 0
                if process.remaining_time > 0:
                    ready_queue.append(idx)
                else:
                    process.completion_time = current_time
                    process.calculate_metrics()
            else:
                # No processes are ready; jump to the next arrival time
                current_time = processes[i].arrival_time

        return processes, gantt_chart

    @staticmethod
    def hpf_non_preemptive(processes: List[Process]) -> Tuple[List[Process], List[Tuple[int, int, int]]]:
        """Non-preemptive Highest Priority First (greatest priority number is highest)"""
        processes = sorted(processes, key=lambda x: x.arrival_time)
        current_time = 0
        gantt_chart = []
        ready_queue = []
        i = 0

        while i < len(processes) or ready_queue:
            while i < len(processes) and processes[i].arrival_time <= current_time:
                heapq.heappush(ready_queue, (-processes[i].priority, i))  # Negative for max heap
                i += 1

            if ready_queue:
                _, idx = heapq.heappop(ready_queue)
                process = processes[idx]
                process.start_time = current_time
                process.completion_time = current_time + process.burst_time
                process.calculate_metrics()
                gantt_chart.append((process.pid, current_time, process.completion_time))
                current_time = process.completion_time
            else:
                current_time = processes[i].arrival_time

        return processes, gantt_chart

    @staticmethod
    def srtf(processes: List[Process]) -> Tuple[List[Process], List[Tuple[int, int, int]]]:
        """Preemptive Shortest Remaining Time First"""
        processes = sorted(processes, key=lambda x: x.arrival_time)
        current_time = 0
        gantt_chart = []
        ready_queue = []
        i = 0
        prev_pid = None

        while i < len(processes) or ready_queue:
            while i < len(processes) and processes[i].arrival_time <= current_time:
                heapq.heappush(ready_queue, (processes[i].remaining_time, processes[i].pid, i))
                i += 1

            if ready_queue:
                remaining, pid, idx = heapq.heappop(ready_queue)
                process = processes[idx]

                if process.start_time is None:
                    process.start_time = current_time

                # Execute for 1 time unit
                if prev_pid != process.pid:
                    if prev_pid is not None and gantt_chart and gantt_chart[-1][0] == prev_pid:
                        # Extend previous block if same process continues
                        gantt_chart[-1] = (prev_pid, gantt_chart[-1][1], current_time + 1)
                    else:
                        gantt_chart.append((process.pid, current_time, current_time + 1))
                    prev_pid = process.pid
                else:
                    gantt_chart[-1] = (process.pid, gantt_chart[-1][1], current_time + 1)

                process.remaining_time -= 1
                current_time += 1

                if process.remaining_time > 0:
                    heapq.heappush(ready_queue, (process.remaining_time, process.pid, idx))
                else:
                    process.completion_time = current_time
                    process.calculate_metrics()
            else:
                current_time = processes[i].arrival_time

        return processes, gantt_chart