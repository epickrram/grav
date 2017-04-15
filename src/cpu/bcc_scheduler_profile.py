#!/usr/bin/python
from bcc import BPF
import json
import sys
import time


if len(sys.argv) < 2:
    print("Usage: %s <duration-seconds>" % (sys.argv[0]))
    sys.exit(1)

prog="""
#include <linux/types.h>
#include <linux/sched.h>
#include <uapi/linux/ptrace.h>

struct scheduled_out_state_t {
    int running;
    int sleeping;
    int uninterruptible;
    int unknown;
};

BPF_TABLE("hash", pid_t, struct scheduled_out_state_t, scheduled_out_states, 1024);

int trace_finish_task_switch(struct pt_regs *ctx, struct task_struct *prev) {

    pid_t prev_pid = prev->pid;
    //pid_t prev_tid = prev->tgid;

    struct scheduled_out_state_t *states = scheduled_out_states.lookup(&prev_pid);
    if (states == 0) {
        struct scheduled_out_state_t new_state = {.running = 0, .sleeping = 0, .uninterruptible = 0, .unknown = 0};
        states = &new_state;
        scheduled_out_states.update(&prev_pid, states);
    }
    
    if (prev->state == 0) {
        states->running++; 
    } else if (prev->state == 1) {
        states->sleeping++;
    } else if (prev->state == 2) {
        states->uninterruptible++;
    } else {
        states->unknown++;
    }

    return 0;
};
"""

b = BPF(text=prog)
b.attach_kprobe(event="finish_task_switch", fn_name="trace_finish_task_switch")

time.sleep(int(sys.argv[1]))
results = dict()
for k,v in b["scheduled_out_states"].iteritems():
    tid_stats = dict()
    tid_stats['R'] = v.running
    tid_stats['S'] = v.sleeping
    tid_stats['D'] = v.uninterruptible
    tid_stats['U'] = v.unknown
    tid_stats['total'] = v.running + v.sleeping + v.uninterruptible + v.unknown
    results[int(k.value)] = tid_stats

    json.dump(results, open('scheduler-states.json', 'w'))
