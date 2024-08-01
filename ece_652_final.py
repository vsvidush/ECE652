import math
import heapq
import sys

class Task:
    def __init__(self, execution_time, period, deadline, id):
        self.execution_time = execution_time
        self.period = period
        self.deadline = deadline
        self.remaining_time = execution_time
        self.next_deadline = deadline
        self.id = id
        self.preemptions = 0

    def __lt__(self, other):
        if self.next_deadline == other.next_deadline:
            return self.id < other.id
        return self.next_deadline < other.next_deadline

def lcm(a, b):
    return abs(a * b) // math.gcd(a, b)

def calculate_hyperperiod(tasks):
    periods = [task.period for task in tasks]
    hyperperiod = periods[0]
    for period in periods[1:]:
        hyperperiod = lcm(int(hyperperiod), int(period))
    return hyperperiod

def read_tasks(file_path):
    tasks = []
    with open(file_path, 'r') as file:
        for id, line in enumerate(file):
            execution_time, period, deadline = map(float, line.strip().split(','))
            tasks.append(Task(execution_time, period, deadline, id))
    return tasks

def simulate_dm_scheduling(tasks, hyperperiod):
    time = 0
    ready_queue = []
    active_task = None

    # Initialize the ready queue with tasks
    for task in tasks:
        heapq.heappush(ready_queue, (task.next_deadline, task))

    while time < hyperperiod:
        # Check for task arrivals
        for task in tasks:
            if time != 0 and time % task.period == 0:
                task.remaining_time = task.execution_time
                task.next_deadline = time + task.deadline
                heapq.heappush(ready_queue, (task.next_deadline, task))

        if active_task and active_task.remaining_time > 0:
            heapq.heappush(ready_queue, (active_task.next_deadline, active_task))

        if ready_queue:
            _, current_task = heapq.heappop(ready_queue)

            # Check for preemption
            if active_task and active_task != current_task and active_task.remaining_time > 0:
                active_task.preemptions += 1
                heapq.heappush(ready_queue, (active_task.next_deadline, active_task))

            active_task = current_task

            # Execute the task
            active_task.remaining_time -= 1

            # If task completes
            if active_task.remaining_time == 0:
                active_task = None

        time += 1

    return tasks

def check_schedulability(tasks, hyperperiod):
    utilization = sum(task.execution_time / task.period for task in tasks)
    return utilization <= 1.0

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 ece_652_final.py <input_file>")
        return

    file_path = sys.argv[1]
    tasks = read_tasks(file_path)
    hyperperiod = calculate_hyperperiod(tasks)
    schedulable = check_schedulability(tasks, hyperperiod)

    if schedulable:
        tasks = simulate_dm_scheduling(tasks, hyperperiod)
        preemptions = [str(task.preemptions) for task in tasks]
        print("1")
        print(",".join(preemptions))
    else:
        print("0")
        print("")

if __name__ == "__main__":
    main()
