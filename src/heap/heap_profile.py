#!/usr/bin/python
from bcc import BPF,USDT

import json
import sys
import time


if len(sys.argv) < 2:
    print("Usage: %s <pid>" % (sys.argv[0]))
    sys.exit(1)


prog="""
#include <linux/types.h>
#include <uapi/linux/ptrace.h>
#include <uapi/linux/bpf_perf_event.h>
#include <linux/sched.h>

struct key_t {
    u32 pid;
    u64 kernel_ip;
    u64 kernel_ret_ip;
    int user_stack_id;
    int kernel_stack_id;
    char name[TASK_COMM_LEN];
};
BPF_HASH(counts, struct key_t);
BPF_HASH(start, u32);
BPF_STACK_TRACE(stack_traces, 10240)

int trace_alloc(void *ctx) {
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    if (!(pid == %s))
        return 0;

    // create map key
    u64 zero = 0, *val;
    struct key_t key = {.pid = pid};
    bpf_get_current_comm(&key.name, sizeof(key.name));

    key.user_stack_id = stack_traces.get_stackid(ctx, 0 | BPF_F_REUSE_STACKID | BPF_F_USER_STACK);
    key.kernel_stack_id = -1;

    val = counts.lookup_or_init(&key, &zero);
    (*val)++;

    return 0;
};
 
"""

# single arg is an oop - need header file from jdk
# http://hg.openjdk.java.net/jdk7u/jdk7u/hotspot/file/f49c3e79b676/src/share/vm/oops/oop.hpp

usdt = USDT(path="/usr/lib/jvm/java-8-openjdk-amd64/jre/lib/amd64/server/libjvm.so", pid=int(sys.argv[1]))
usdt.enable_probe(probe="object__alloc", fn_name="trace_alloc")
bpf = BPF(text=prog % (int(sys.argv[1])), usdt_contexts=[usdt])


time.sleep(5)
stack_traces = bpf["stack_traces"]
for k, v in bpf["counts"].iteritems():
    print "%d allocations at" % v.value
    for addr in stack_traces.walk(k.user_stack_id):
        pid = k.pid
        print bpf.sym(addr, pid) + (" (from raw %-16x " % addr) + ")"


