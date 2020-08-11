import os
from typing import List
from src.handlers.request_schema import Disitribution
import random


DATA_DIRECTORY = "data"

class AttachmentRandomiser:
    def __init__(self):
        self.attachments_sent = 0
        self.files_loaded = []
        self.total_weight = 0
        self.curr_selected = None
        self.distribution = None
        self.running_total_weight = 0


    def load_all_attachments_to_memory(self):
        # Load Everything from data
        result = os.path.isdir(DATA_DIRECTORY)
        if result == True:
            items = os.listdir(DATA_DIRECTORY)
            self.files_loaded = items
        else:
            raise OSError("data directory not found")

    def import_distribution(self, distribution: List[Disitribution]):
        self.distribution = distribution
        for item in distribution:
            self.total_weight += item.weight
            self.files_loaded.append(item.file)

    def select_random_attachment(self):
        if self.curr_selected == None:
            self.curr_selected = self.files_loaded[0]
        self.running_total_weight = self.running_total_weight
        for item in self.distribution:
            r = random.randint(0, self.running_total_weight + item.weight )
            if r >= self.running_total_weight:
                self.curr_selected = item.file
            self.running_total_weight += item.weight
        return self.curr_selected
