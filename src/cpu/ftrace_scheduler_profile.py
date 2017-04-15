#!/usr/bin/python

import json
import re
import sys


def get_thread_scheduling():
    thread_scheduling = dict()
    total_samples = dict()

    # TODO add stat_runtime
    for line in sys.stdin:
        if line.find("sched_switch") > -1:
            tokens = re.split("\s+", line.strip())
            tid = int(tokens[0][tokens[0].rfind("-") + 1:])
            if tid not in thread_scheduling:
                counts = dict()
                counts['R'] = 0
                counts['S'] = 0
                counts['D'] = 0
                counts['U'] = 0
                counts['total'] = 0
                thread_scheduling[tid] = counts
                total_samples[tid] = 0

            outgoing_state = tokens[6]
            if outgoing_state not in ['R', 'S', 'D']:
                print "unknown state: " + str(outgoing_state)
                thread_scheduling[tid]['U'] += 1
            else:
                thread_scheduling[tid][outgoing_state] += 1
            total_samples[tid] += 1
            thread_scheduling[tid]['total'] += 1

    return (thread_scheduling, 0)


if __name__ == "__main__":
    thread_scheduling, max_sample_count = get_thread_scheduling()

    json.dump(thread_scheduling, open('scheduler-states.json', 'w'))
