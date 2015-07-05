import matplotlib.pyplot as plt
import matplotlib.collections as collections
import numpy as np
from operator import itemgetter

global annList
global currentList

class Annotations:
    labels = []
    value = []
    state = []

    def add_label(self, value, state, frame):
        self.labels.append([frame, value, state])

    def add_value(self, _value)
        if _value not in self.value:
            value.append(_value)
            return True
        return False

    def add_state(self, _state)
        if _state not in self.state:
            state.append(_state)
            return True
        return False
    def remove_label(self, frame):
        for item in self.labels:
            if item[0] == frame:
                self.labels.remove(item)
                return True
        return False


