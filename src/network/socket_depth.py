#!/usr/bin/python

## Heavily inspired by /usr/share/bcc/tools/tcptop


import sys
import time
import datetime
from bcc import BPF
from socket import inet_ntop, AF_INET, AF_INET6
from struct import pack


prog="""
#include <linux/types.h>
#include <uapi/linux/ptrace.h>
#include <uapi/linux/bpf_perf_event.h>
#include <linux/sched.h>
#include <linux/socket.h>
#include <net/sock.h>
#include <asm/atomic.h>

struct ipv4_key_t {
    u32 saddr;
    u32 daddr;
    u16 lport;
    u16 dport;
};
BPF_HASH(total_rcv_mem, struct ipv4_key_t);
BPF_HASH(peak_rcv_mem, struct ipv4_key_t);

int trace_socket_rcv(struct pt_regs *ctx, struct sock *sk, struct sk_buff *skb) {
    u16 dport = 0, family = sk->__sk_common.skc_family;

    if (family == AF_INET) {
        struct ipv4_key_t ipv4_key = {};
        ipv4_key.saddr = sk->__sk_common.skc_rcv_saddr;
        ipv4_key.daddr = sk->__sk_common.skc_daddr;
        ipv4_key.lport = sk->__sk_common.skc_num;
        dport = sk->__sk_common.skc_dport;
        ipv4_key.dport = ntohs(dport);
        u64 zero = 0, *total, *max;
        int rmem = sk->sk_rmem_alloc.counter;
        total = total_rcv_mem.lookup_or_init(&ipv4_key, &zero);
        (*total) += rmem + skb->data_len;
        max = peak_rcv_mem.lookup_or_init(&ipv4_key, &zero);
        if (rmem > (*max)) {
            (*max) = rmem + skb->data_len;
        }
    }

    return 0;
};

 
"""

bpf = BPF(text=prog)
bpf.attach_kprobe(event="tcp_v4_do_rcv", fn_name="trace_socket_rcv")

def to_socket_key(k):
        return inet_ntop(AF_INET, pack("I", k.saddr)) + ":" + str(k.lport) + "," + inet_ntop(AF_INET, pack("I", k.daddr)) + ":" + str(k.dport)

with open("/tmp/tcpv4-peak.csv", "a+", 0) as p:
    with open("/tmp/tcpv4-total.csv", "a+", 0) as t:

        while True:

            time.sleep(1)
            current_time = datetime.datetime.now()
            total_depth = bpf["total_rcv_mem"]
            max_depth = bpf["peak_rcv_mem"]
            if len(total_depth) == 0 and len(max_depth) == 0:
                print "No data captured"

            else:
                for socket, total in total_depth.iteritems():
                    t.write("{0},{1},{2},{3}\n".format(current_time.strftime("%H:%M:%S"), current_time.strftime("%s"), to_socket_key(socket), total.value))
                for socket, peak in max_depth.iteritems():
                    p.write("{0},{1},{2},{3}\n".format(current_time.strftime("%H:%M:%S"), current_time.strftime("%s"), to_socket_key(socket), peak.value))
                total_depth.clear()
                max_depth.clear()


