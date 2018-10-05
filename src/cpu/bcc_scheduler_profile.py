#!/usr/bin/python
from bcc import BPF
import json
import sys
import time


if len(sys.argv) < 3:
    print("Usage: %s <pid> <duration-seconds>" % (sys.argv[0]))
    sys.exit(1)

# Task states taken from http://lxr.free-electrons.com/source/include/linux/sched.h?v=4.4#L207
# Character codes taken from http://lxr.free-electrons.com/source/include/trace/events/sched.h?v=4.4#L155

prog="""
#include <linux/types.h>
#include <linux/sched.h>
#include <uapi/linux/ptrace.h>

struct scheduled_out_state_t {
    int running;
    int sleeping;
    int uninterruptible;
    int traced;
    int stopped;
    int parked;
    int idle;
    int unknown;
    int dead;
    int wake_kill;
    int unknown_state_0;
    int total;
};

struct proc_counter_t {
    int count;
    char proc_name[TASK_COMM_LEN];
};

BPF_TABLE("hash", pid_t, struct proc_counter_t, usurpers, 1024);
BPF_TABLE("hash", pid_t, struct scheduled_out_state_t, scheduled_out_states, 1024);

TRACEPOINT_PROBE(sched, sched_switch) {
    pid_t prev_pid = args->prev_pid;

    struct scheduled_out_state_t *states = scheduled_out_states.lookup(&prev_pid);
    if (states == 0) {
        struct scheduled_out_state_t new_state = {.running = 0, .sleeping = 0, .uninterruptible = 0, .unknown = 0};
        states = &new_state;
        scheduled_out_states.update(&prev_pid, states);
    }
   
    // 4, 64, 32

    // TODO consider switch statement
    states->total++;
    if (args->prev_state == TASK_RUNNING) {
        states->running++;
    } else if (args->prev_state == TASK_INTERRUPTIBLE) { // "An Interruptible sleep state means the process is waiting either for a particular time slot or for a particular event to occur."
        states->sleeping++;
    } else if (args->prev_state == TASK_UNINTERRUPTIBLE) { // "The Uninterruptible state is mostly used by device drivers waiting for disk or network I/O."
        states->uninterruptible++;
    } else if (args->prev_state == __TASK_TRACED || args->prev_state == TASK_TRACED) {
        states->traced++;
    } else if (args->prev_state == __TASK_STOPPED || args->prev_state == TASK_STOPPED) {
        states->stopped++;
    } else if (args->prev_state == TASK_PARKED) {
        states->parked++;
    } else if ((args->prev_state & (TASK_DEAD | EXIT_ZOMBIE | EXIT_DEAD)) != 0) {
        states->dead++;
    } else if ((args->prev_state & TASK_WAKEKILL) != 0) {
        states->wake_kill++;
    } else {
        states->unknown++;
        states->unknown_state_0 = args->prev_state;
    }

    return 0;
};
"""


SHOULD_TRACK_USURPERS = 0

b = BPF(text=prog)

time.sleep(int(sys.argv[2]))

scheduling_states = dict()
for k,v in b["scheduled_out_states"].iteritems():
    tid_stats = dict()
    tid_stats['R'] = v.running
    tid_stats['S'] = v.sleeping
    tid_stats['D'] = v.uninterruptible
    tid_stats['Tr'] = v.traced
    tid_stats['St'] = v.stopped
    tid_stats['P'] = v.parked
    tid_stats['x'] = v.dead
    tid_stats['K'] = v.wake_kill
    tid_stats['U'] = v.unknown
    if v.unknown_state_0 != 0:
        print(v.unknown_state_0)
    total = v.total
    tid_stats['total'] = total
    if total != 0:
        scheduling_states[int(k.value)] = tid_stats

json.dump(scheduling_states, open(sys.argv[3], 'w'))

if SHOULD_TRACK_USURPERS == 1:
    # TODO add parent pid to record
    contending_commands = dict()
    for k, v in b["usurpers"].iteritems():
        key = v.proc_name + "/" + str(k.value)
        if key not in contending_commands:
            contending_commands[key] = 0
        contending_commands[key] += 1

    json.dump(contending_commands, open(sys.argv[4], 'w'))
