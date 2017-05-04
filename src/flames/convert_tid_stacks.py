#!/usr/bin/python

import re
import sys


def get_tid_to_thread_name(jstack_file):
    tid_to_thread_name = dict()
    for line in open(jstack_file):
        if line.find("nid=") != -1:
            try:
                hex_tid = line.split('nid=')[1].split(" ")[0]
                thread_name = line.split('"')[1]
                decimal_tid = int(hex_tid, 0)
                tid_to_thread_name[decimal_tid] = thread_name
            except IndexError:
                print "Failed to parse tid from line: " + line

    return tid_to_thread_name


def get_aggregation_candidate_thread_prefixes(tid_to_thread_name):
    prefix_counts = dict()
    for thread_name in tid_to_thread_name.itervalues():
        if thread_name.find("-") > -1:
            prefix = thread_name[0:thread_name.rfind("-")]
            if prefix not in prefix_counts:
                prefix_counts[prefix] = 0
            prefix_counts[prefix] += 1

    candidates = set()
    for prefix, count in prefix_counts.iteritems():
        if count > 1:
            candidates.add(prefix)
    return candidates


def get_aggregate_name(thread_name, candidates):
    for candidate in candidates:
        if thread_name.find(candidate) == 0:
            return candidate
    return None


def replace_tids_with_names(collapsed_stack_file, output_file, tid_to_thread_name, regex, aggregate_on_thread_prefix):
    aggregation_candidates = get_aggregation_candidate_thread_prefixes(tid_to_thread_name)
    out = open(output_file, 'w')
    for line in open(collapsed_stack_file):
        try:
            for tid in tid_to_thread_name:
                if line.find("/" + str(tid) + ";") > -1:
                    thread_name = tid_to_thread_name[tid]
                    aggregation_candidate = get_aggregate_name(thread_name, aggregation_candidates)
                    if aggregation_candidate is not None and aggregate_on_thread_prefix:
                        thread_name = aggregation_candidate + "-*"
                    line = line.replace("/" + str(tid) + ";", "/" + thread_name + ";")
            if regex is not None and line.find(";") > 0:
                search_substring = line[:line.find(";")]
                if regex.search(search_substring) is not None:
                    out.write(line)
            else:
                out.write(line)
        except ValueError:
            print "Failed to parse pid from line: " + line
    out.flush()


if __name__ == "__main__":
    jstack_file = sys.argv[1]
    stacks_file = sys.argv[2]
    output_file = sys.argv[3]
    regex_pattern = sys.argv[4]
    if regex_pattern == "NOT_SET":
        regex = None
    else:
        regex = re.compile("\/" + regex_pattern)
    aggregate_on_thread_prefix = "True" == sys.argv[5]

    if aggregate_on_thread_prefix:
        print "Aggregating stacks on thread prefix"
    else:
        print "Not aggregating stacks on thread prefix, enable by setting AGGREGATE_ON_THREAD_PREFIX=True"

    tid_to_thread_name = get_tid_to_thread_name(jstack_file)
    replace_tids_with_names(stacks_file, output_file, tid_to_thread_name, regex, aggregate_on_thread_prefix)
