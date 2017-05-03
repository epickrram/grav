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


def replace_tids_with_names(collapsed_stack_file, output_file, tid_to_thread_name, regex):
    out = open(output_file, 'w')
    for line in open(collapsed_stack_file):
        try:
            for tid in tid_to_thread_name:
                line = line.replace("/" + str(tid) + ";", "/" + tid_to_thread_name[tid] + ";")
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
    tid_to_thread_name = get_tid_to_thread_name(jstack_file)
    replace_tids_with_names(stacks_file, output_file, tid_to_thread_name, regex)
