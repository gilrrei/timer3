"""Timer3."""
import time
from contextlib import contextmanager
from functools import wraps, partial
import csv


class Timer3:
    """Class to time functions or construct timer context."""

    def __init__(self):
        self.times = []
        self.names = []
        self.states = []
        self.current_state = -1
        self.order = []

    def timethis(self, log_function=None, name=None):
        """Decorator factory to time functions."""

        def decorator(fun, name, log_function):
            if name is None:
                name = fun.__qualname__

            @wraps(fun)
            def inner(*args, **kwargs):
                with self.time(name=name, log_function=log_function):
                    return fun(*args, **kwargs)

            return inner

        return partial(decorator, name=name, log_function=log_function)

    @contextmanager
    def time(self, name, log_function=None):
        """Context for timing."""
        if log_function:
            log_function("Starting " + name)
        self.current_state += 1
        start_time = time.perf_counter()
        yield
        total_time = time.perf_counter() - start_time
        self.states.append(self.current_state)
        self.times.append(total_time)
        self.names.append(name)
        self.order.append(len(self.order))
        self.current_state -= 1
        if log_function:
            log_function(name + f" done, took {total_time}s")

    def sort_by_call_order(self, states=None, ids=None, current_state=0):
        """Sort by correct call order."""
        if states is None:
            states = self.states
        if ids is None:
            ids = range(len(states))
        current_state_indices = [
            ids[i] for i, j in enumerate(states) if j == current_state
        ]
        nested_states = []
        subcall_states = []
        sorted_ids = []
        subcall_ids = []
        for id_state, state in zip(ids, states):
            if id_state in current_state_indices:

                # Add the new state
                sorted_ids.extend([id_state])
                nested_states.append([current_state])

                # In case of subcalls
                if len(subcall_ids) > 0:

                    # Order the subcalls
                    subcall_states, subcall_ids = self.sort_by_call_order(
                        subcall_states, subcall_ids, current_state=current_state + 1
                    )

                    # Add the subcalls
                    nested_states.append(subcall_states)
                    sorted_ids.extend(subcall_ids)

                    # Reset subcalls
                    subcall_states = []
                    subcall_ids = []

            else:
                # Update subcalls
                subcall_ids.extend([id_state])
                subcall_states.append(state)

        # If last only return index
        if current_state == 0:
            return sorted_ids

        # For recursion add the nested states
        return nested_states, sorted_ids

    def __str__(self):
        """Create timer table."""
        string = ""
        max_len = min(40, max([len(n) + s for n, s in zip(self.names, self.states)]))
        row_format = f"| {{:<{max_len+4}}} {{:.8E}} |\n"
        separator = "+" + "-" * (max_len + 21) + "+"
        string = separator + "\n"
        string += "| " + "Timer3".center(len(separator) - 4) + " |\n"
        string += separator + "\n"
        for i in self.sort_by_call_order():
            n, t, s = self.names[i], self.times[i], self.states[i]
            string += row_format.format(" " * s + n, t)
        string += separator + "\n"
        return string

    def export_csv(self, file_path):
        """Export timer three to csv."""
        max_state = max(self.states) + 1
        with open(file_path, "w", newline="") as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=",")
            row = [""] * max_state + ["time (s)"]
            row[0] = "function names"
            csv_writer.writerow(row)
            for i in self.sort_by_call_order():
                n, t, s = self.names[i], self.times[i], self.states[i]
                row = [""] * max_state + [t]
                row[s] = n
                csv_writer.writerow(row)
