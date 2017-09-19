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

int trace_finish_task_switch(struct pt_regs *ctx, struct task_struct *prev) {
    int pid_to_record = %d;
    int should_track_usurpers = %d;

    pid_t prev_pid = prev->pid;
    pid_t parent_pid = prev->parent->pid;
    pid_t incoming_pid = bpf_get_current_pid_tgid();
    // only works on newer kernels (e.g. 4.10)
    if (should_track_usurpers) {
        struct task_struct *task;
        task = (struct task_struct *)bpf_get_current_task();
        pid_t current_parent_pid = task->parent->pid;
        
        struct proc_counter_t *counter = usurpers.lookup(&incoming_pid);
        if (counter == 0) {
            struct proc_counter_t new_counter = {.proc_name = NULL, .count = 0};
            bpf_get_current_comm(&new_counter.proc_name, sizeof(new_counter.proc_name));
            counter = &new_counter;
            usurpers.update(&incoming_pid, counter);
        }
        if (prev->state == 0) {
            counter->count++;
        }
    }
    
    struct scheduled_out_state_t *states = scheduled_out_states.lookup(&prev_pid);
    if (states == 0) {
        struct scheduled_out_state_t new_state = {.running = 0, .sleeping = 0, .uninterruptible = 0, .unknown = 0};
        states = &new_state;
        scheduled_out_states.update(&prev_pid, states);
    }
    
    // TODO consider switch statement
    states->total++;
    if (prev->state == 0) {
        states->running++; 
    } else if (prev->state == 1) {
        states->sleeping++;
    } else if (prev->state == 2) {
        states->uninterruptible++;
    } else if ((prev->state | 64) != 0) {
        states->dead++;
    } else if ((prev->state | 128) != 0) {
        states->wake_kill++;
    } else {
        states->unknown++;
        states->unknown_state_0 = prev->state;
    }

    return 0;
};
"""

SHOULD_TRACK_USURPERS = 0

b = BPF(text=prog % (int(sys.argv[1]), SHOULD_TRACK_USURPERS))
b.attach_kprobe(event="finish_task_switch", fn_name="trace_finish_task_switch")

time.sleep(int(sys.argv[2]))

scheduling_states = dict()
for k,v in b["scheduled_out_states"].iteritems():
    tid_stats = dict()
    tid_stats['R'] = v.running
    tid_stats['S'] = v.sleeping
    tid_stats['D'] = v.uninterruptible
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
