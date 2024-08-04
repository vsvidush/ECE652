import math
import heapq
import sys

class Task:
    def __init__(self, execution_time, period, deadline, id, scale_factor):
        self.execution_time = execution_time
        self.period = period
        self.deadline = deadline
        self.remaining_time = execution_time
        self.next_deadline = deadline
        self.id = id
        self.preemptions = 0
        self.scale_factor = scale_factor

    def __lt__(self, other):
        if self.next_deadline == other.next_deadline:
            return self.id < other.id
        return self.next_deadline < other.next_deadline

def lcm(a, b):
    return abs(a * b) // math.gcd(a, b)

def hcf(a, b):
    return math.gcd(a, b)

# calculate hyperperiod

def calculate_hyperperiod(tasks):
    periods = [task.period for task in tasks]
    hyperperiod = periods[0]
    for period in periods[1:]:
        hyperperiod = lcm(int(hyperperiod), int(period))
    return hyperperiod

def read_tasks(file_path):
    tasks = []
    max_decimal_places = 0

    # First pass to determine the maximum number of decimal places
    with open(file_path, 'r') as file:
        for line in file:
            execution_time, period, deadline = map(float, line.strip().split(','))
            max_decimal_places = max(max_decimal_places, 
                                     *[len(str(f).split('.')[1]) if '.' in str(f) else 0 for f in [execution_time, period, deadline]])

    scale_factor = 10 ** max_decimal_places

    # Second pass to read and scale the tasks
    with open(file_path, 'r') as file:
        for id, line in enumerate(file):
            execution_time, period, deadline = map(float, line.strip().split(','))
            execution_time = int(execution_time * scale_factor)
            period = int(period * scale_factor)
            deadline = int(deadline * scale_factor)
            tasks.append(Task(execution_time, period, deadline, id, scale_factor))

    return tasks, scale_factor

def simulate_dm_scheduling(tasks, hyperperiod, time_unit, scale_factor):
    time = 0
    ready_queue = []
    active_task = None

    # Initialize the ready queue with tasks
    for task in tasks:
        heapq.heappush(ready_queue, (task.next_deadline, task))

    while time < hyperperiod:
        # Check for task arrivals
        for task in tasks:
            if time % task.period == 0 and time != 0:
                task.remaining_time = task.execution_time
                task.next_deadline = time + task.deadline
                heapq.heappush(ready_queue, (task.next_deadline, task))

        if active_task and active_task.remaining_time > 0:
            heapq.heappush(ready_queue, (active_task.next_deadline, active_task))

        if ready_queue:
            _, current_task = heapq.heappop(ready_queue)

            # Check for preemption
            if active_task and active_task != current_task:
                active_task.preemptions += 1

            active_task = current_task

            # Execute the task
            active_task.remaining_time -= time_unit  # Adjusted for the minimum time unit

            # Ensure remaining time does not become negative
            if active_task.remaining_time < 0:
                active_task.remaining_time = 0

            # Print execution details
            #print(f"Time {time / scale_factor:.3f}: Task {active_task.id} executes, remaining time {active_task.remaining_time / scale_factor:.3f}")

            # If task completes
            if active_task.remaining_time <= 0:
                active_task = None

        time += time_unit  # Adjusted for the minimum time unit

def check_schedulability(tasks, hyperperiod):
    utilization = sum(task.execution_time / task.period for task in tasks)
    return utilization <= 1.0

def main():
    if len(sys.argv) != 2:
        print("Usage: python ece_652_diagnosis2.py <input_file>")
        return

    file_path = sys.argv[1]
    tasks, scale_factor = read_tasks(file_path)
    hyperperiod = calculate_hyperperiod(tasks)
    
    # Calculate HCF of scaled execution times
    scaled_execution_times = [task.execution_time for task in tasks]
    hcf_execution_time = scaled_execution_times[0]
    for time in scaled_execution_times[1:]:
        hcf_execution_time = hcf(hcf_execution_time, time)

    schedulable = check_schedulability(tasks, hyperperiod)

    #print(f"LCM (Hyperperiod): {hyperperiod / scale_factor:.3f}")
    #print(f"HCF of execution times: {hcf_execution_time / scale_factor:.3f}")
    #print("Task priorities based on deadlines:")
    #for task in sorted(tasks, key=lambda t: t.deadline):
        #print(f"Task {task.id}: Deadline {task.deadline / scale_factor:.3f}, Period {task.period / scale_factor:.3f}")

    if schedulable:
        simulate_dm_scheduling(tasks, hyperperiod, hcf_execution_time, scale_factor)
        preemptions = [str(task.preemptions) for task in tasks]
        print("1")
        print(",".join(preemptions))
    else:
        print("0")
        print("")

if __name__ == "__main__":
    main()
