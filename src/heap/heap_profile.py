#!/usr/bin/python
import sys
import time
from bcc import BPF, USDT

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
    int user_stack_id;
    char name[256];
};
BPF_HASH(counts, struct key_t);
BPF_HASH(start, u32);
BPF_HASH(tids, long);
BPF_STACK_TRACE(stack_traces, 10240)

int trace_alloc(struct pt_regs *ctx, long tid, char *name, int nameLength, int wordSize) {
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    // not really necessary, as USDT attaches to pid
    if (!(pid == %s))
        return 0;


    u64 zero = 0, *val, *tc;
    struct key_t key = {.pid = pid};
    bpf_probe_read(&key.name, sizeof(key.name), (void *)PT_REGS_PARM3(ctx));

    tc = tids.lookup_or_init(&tid, &zero);
    (*tc)++;

    key.user_stack_id = stack_traces.get_stackid(ctx, 0 | BPF_F_REUSE_STACKID | BPF_F_USER_STACK);

    val = counts.lookup_or_init(&key, &zero);
    (*val)++;

    return 0;
};
 
"""

# single arg is an oop - need header file from jdk
# http://hg.openjdk.java.net/jdk7u/jdk7u/hotspot/file/f49c3e79b676/src/share/vm/oops/oop.hpp
pid=int(sys.argv[1])
usdt = USDT(path="/usr/lib/jvm/java-8-openjdk-amd64/jre/lib/amd64/server/libjvm.so", pid=int(sys.argv[1]))
usdt.enable_probe(probe="object__alloc", fn_name="trace_alloc")
bpf = BPF(text=prog % (int(sys.argv[1])), usdt_contexts=[usdt])


time.sleep(5)

if len(bpf["tids"]) == 0:
    print "No data found - are DTrace probes enabled in running process?"

stack_traces = bpf["stack_traces"]
all_stacks=[]
stack_counts=dict()

for k, v in bpf["counts"].iteritems():
    stack=[]
    for addr in stack_traces.walk(k.user_stack_id):
        pid = k.pid
        symbol=bpf.sym(addr, pid)
        if symbol == "[unknown]":
            stack.append(("0x%-16x" % addr).strip())
        else:
            stack_trace_entry = symbol.strip().replace(';',':')
            if stack_trace_entry[0] == 'L' and stack_trace_entry.find(':::'):
                stack_trace_entry = stack_trace_entry[1:]
            stack.append(stack_trace_entry)
    stack.reverse()
    try:
        stack_counts[k.name.strip().encode('utf-8', errors='replace') + ";" + ";".join(stack).encode('utf-8', errors='replace')] = int(v.value)
    except UnicodeDecodeError:
        print "Failed to decode stack: " + str(stack)



for k, v in stack_counts.iteritems():
    print k + " " + str(v)


