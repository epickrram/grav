#!/usr/bin/python

import re
import sys

CPU_COLOURS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
#perf script -F comm,pid,tid,cpu,time,event

def get_cpu_tenancy_count_by_tid():
    pid_map = dict()
    max_sample_count = 0
    line_count = 0
    
    for line in sys.stdin:
        try:
            line_count += 1
            tokens = re.split("\s+", line.strip())
            process_id = re.search("([0-9]+)/([0-9]+)", tokens[1].strip())
            if process_id is not None:
                pid = int(process_id.group(1))
                tid = int(process_id.group(2))

                if pid not in pid_map:
                    pid_map[pid] = dict()
                tid_map = pid_map[pid]
                if tid not in tid_map:
                    tid_map[tid] = dict()
                cpu_sample_count = tid_map[tid]
                cpu_id = int(re.search("\[([0-9]+)\]", tokens[2]).group(1))
           
                if 'all' not in cpu_sample_count:
                    cpu_sample_count['all'] = 0
                if cpu_id not in cpu_sample_count:
                    cpu_sample_count[cpu_id] = 0
                cpu_sample_count[cpu_id] += 1
                cpu_sample_count['all'] += 1

                if cpu_sample_count['all'] > max_sample_count:
                    max_sample_count = cpu_sample_count['all']

        except AttributeError:
            print "failed to parse line: " + line

    return (pid_map, max_sample_count)

def write_svg_header(writer, width, height):
    writer.write('<?xml version="1.0" standalone="no"?><!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">')
    writer.write('<svg version="1.1" width="' + str(width) + '" height="' + str(height) + '"  xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">\n')

def write_svg_footer(writer):
    writer.write('</svg>\n')

def calculate_number_of_columns(cpu_tenancy_by_pid):
    column_count = 0
    for pid in cpu_tenancy_by_pid:
        column_count += len(cpu_tenancy_by_pid[pid])
    return column_count

def get_fill(cpu_id):
    # TODO support 256 cpus
    return CPU_COLOURS[cpu_id % len(CPU_COLOURS)]

def write_cell(writer, x_offset, y_offset, width, height, cpu_id, tid):
    thread_name = str(tid)
    cell_text = '{}/CPU{}'.format(thread_name, cpu_id)
    writer.write('<g><title>{}</title>'.format(cell_text))
    writer.write('<rect x="{}" y="{}" width="{}" height="{}" fill="{}">'.format(x_offset, y_offset, width, height, get_fill(cpu_id)))
    writer.write('</rect>\n')
    #writer.write('<text x="{}" y="{}" font-size="12" font-family="monospace" fill="#000">{}</text>'.format(x_offset, y_offset + 12, "CPU" + str(cpu_id)))
    writer.write('</g>\n')

def write_svg(width, height, cpu_tenancy_by_pid, max_sample_count, tid_to_thread_name):
    writer = open('test.svg', 'w')
    write_svg_header(writer, width, height)

    column_width = float(width / calculate_number_of_columns(cpu_tenancy_by_pid))
    single_sample_height = float(height / float(max_sample_count))

    x_offset = 0
    y_offset = height
    thread_name_to_tid = dict()
    for t in tid_to_thread_name:
        thread_name_to_tid[tid_to_thread_name[t]] = t
    for pid in sorted(cpu_tenancy_by_pid.iterkeys()):
        for tid in sorted(cpu_tenancy_by_pid[pid].iterkeys()):
            cpu_sample_count = cpu_tenancy_by_pid[pid][tid]
            y_offset = height
            for cpu_id in sorted(cpu_sample_count.iterkeys()):
                if cpu_id is not 'all':
                    sample_height = single_sample_height * cpu_sample_count[cpu_id]
                    thread_name = "unknown"
                    if tid in tid_to_thread_name:
                        thread_name = tid_to_thread_name[tid]
                    write_cell(writer, x_offset, y_offset - sample_height, column_width, sample_height, cpu_id, thread_name)
                    y_offset -= sample_height

            x_offset += column_width
                
    write_svg_footer(writer)
    writer.close()

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


if __name__ == "__main__":
    tid_to_thread_name = get_tid_to_thread_name(sys.argv[1])
    cpu_tenancy_by_pid, max_sample_count = get_cpu_tenancy_count_by_tid()

    write_svg(1200, 600, cpu_tenancy_by_pid, max_sample_count, tid_to_thread_name)
