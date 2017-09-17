#!/usr/bin/python

import argparse
import re
import sys
import time
from bcc import BPF, USDT

# minimum amount of total allocations for an object to be included in the flamegraph
MIN_ALLOCATION_SHARE_PERCENTAGE=1

def apply_regex(stack_counts, regex_list, should_include):
    if regex_list is None:
        return stack_counts
    filtered_stack_counts=dict()
    if should_include is False:
        filtered_stack_counts=dict(stack_counts)
    for pattern in regex_list:
        regex = re.compile(pattern)
        for k, v in stack_counts.iteritems():
            if should_include and regex.search(k) is not None:
                filtered_stack_counts[k] = v
            elif should_include is False and regex.search(k) is not None:
                if k in filtered_stack_counts:
                    del filtered_stack_counts[k]
    return filtered_stack_counts

def apply_exclusion_regex(stack_counts, regex_list):
    return apply_regex(stack_counts, regex_list, False)

def apply_inclusion_regex(stack_counts, regex_list):
    return apply_regex(stack_counts, regex_list, True)

def remove_objects_with_small_allocation_count(stack_counts):
    alloc_count_by_class = dict()
    total_allocations = 0
    large_allocations = dict()
    for k, v in stack_counts.iteritems():
        class_name = k.split(";")[0]
        if class_name not in alloc_count_by_class:
            alloc_count_by_class[class_name] = v
        else:
            alloc_count_by_class[class_name] += v
        total_allocations += v
    
    for k, v in stack_counts.iteritems():
        
        class_name = k.split(";")[0]
        percentage_of_allocations = (alloc_count_by_class[class_name] * 100) / float(total_allocations)
        if percentage_of_allocations > MIN_ALLOCATION_SHARE_PERCENTAGE:
            large_allocations[k] = v
    return large_allocations

def remove_non_ascii(text):
    return ''.join(i for i in text if ord(i)<128)


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

def get_arg_parser():
    parser = argparse.ArgumentParser(description = 'Generate heap allocation flamegraphs')

    parser.add_argument('-j', type=str, dest='lib_jvm_path', help='Path to libjvm.so', default='/usr/lib/jvm/java-8-openjdk-amd64/jre/lib/amd64/server/libjvm.so')
    parser.add_argument('-p', type=int, dest='pid', help='PID of the target process', required=True)
    parser.add_argument('-i', type=str, dest='include_regex', help='Regex for stacks to include', nargs='*')
    parser.add_argument('-e', type=str, dest='exclude_regex', help='Regex for stacks to exclude', nargs='*')
    parser.add_argument('-s', type=int, dest='sampling_interval_micros', help='Sampling interval in microseconds')
    parser.add_argument('-d', type=int, dest='duration_seconds', help='Recording duration in seconds', default=10)

    return parser

args = get_arg_parser().parse_args()

pid = args.pid
usdt = USDT(path=args.lib_jvm_path, pid=args.pid)
usdt.enable_probe(probe="object__alloc", fn_name="trace_alloc")
bpf = BPF(text=prog, usdt_contexts=[usdt])


time.sleep(float(str(args.duration_seconds)))

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
            stack.append(stack_trace_entry.encode('utf-8', errors='replace'))
    stack.reverse()
    try:
        key_name = remove_non_ascii(k.name).strip().encode('utf-8', errors='replace')
        stack_counts[key_name + ";" + u";".join(stack).encode('utf-8', errors='replace')] = int(v.value)
    except UnicodeDecodeError as e:
        err_msg = str(e)
        print "Failed to decode stack: " + k.name.strip() + ";" + str(stack) + ": " + err_msg


stack_counts = remove_objects_with_small_allocation_count(stack_counts)
stack_counts = apply_inclusion_regex(stack_counts, args.include_regex)
stack_counts = apply_exclusion_regex(stack_counts, args.exclude_regex)
for k, v in stack_counts.iteritems():
    print k + " " + str(v)


