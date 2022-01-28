"""
Manually added file of forked version. Only contains the ExecutionCounter-class.
"""

import time

class ExecutionCounter():
    """
    Counter and time measurement class.
    """

    def __init__(self):
        self.execution_counter = 0
        self.timestamps = []

    def add(self, num):
        self.execution_counter += num
        timestamp_entry_template = [{
            "timestamp_pre_compile": time.time(),
            "timestamp_post_compile": time.time(),
            "timestamp_post_execution": time.time()
        } for _ in range(num)]
        self.timestamps.extend(timestamp_entry_template)

    def stamp(self, execution_number, stage):
        self.timestamps[execution_number - 1][f"timestamp_{stage}"] = time.time()

    def get_time_delta(self, low_execution_number, high_execution_number, low_stage, high_stage):
        high_stamp = self.timestamps[high_execution_number - 1][f"timestamp_{high_stage}"]
        low_stamp = self.timestamps[low_execution_number - 1][f"timestamp_{low_stage}"]
        return high_stamp - low_stamp