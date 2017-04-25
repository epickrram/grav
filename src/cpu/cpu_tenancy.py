#!/usr/bin/python

import re
import sys

CPU_COLOURS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
#perf script -F comm,pid,tid,cpu,time,event

def init_colours():
    lighter = []
    darker = []
    r = 128
    g = 94
    b = 64
    # use top +- 64
    # gives 128 in each domain
    delta = 16
    while r < 200:
        g = 92
        while g < 205:
            b = 74
            while b < 200:
                lighter.append('{},{},{}'.format(r, g, b))
                darker.append('{},{},{}'.format(r - 16, g - 16, b - 16))
                b += delta
            g += delta
        r += delta

    lighter.reverse()
    darker.reverse()

    print len(lighter)

    return [lighter, darker]

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
    writer.write(
        '<text text-anchor="middle" x="{}" y="30" font-size="20" font-family="monospace" fill="#000">Thread CPU tenancy</text>'.format(width / 2))

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


def overlay_thread_name(writer, x_offset, y_offset, thread_name):
    writer.write('<text x="{}" y="{}" width="{}" font-size="12" font-family="monospace" style="text-overflow: clip" fill="#000">{}</text>'.format(x_offset, y_offset + 12, 1000, thread_name))


def write_cell(writer, x_offset, y_offset, width, height, cpu_id, tid, percentage, colours):
    thread_name = str(tid)
    cell_text = '{}/CPU{} ({:.2f}%)'.format(thread_name, cpu_id, percentage)
    writer.write('<g><title>{}</title>'.format(cell_text))
    fill = colours[0][(cpu_id * 8) % len(colours[0])]
    stroke = colours[1][(cpu_id * 8) % len(colours[1])]
    writer.write('<rect x="{}" y="{}" width="{}" height="{}" fill="rgb({})" stroke="rgb({})">'.format(x_offset, y_offset, width, height, fill, stroke))
    writer.write('</rect>\n')
    writer.write('<text x="{}" y="{}" width="{}" font-size="12" font-family="monospace" style="text-overflow: clip" fill="#000">{}</text>'.format(x_offset, y_offset + 22, width, "CPU{}".format(cpu_id)))
    writer.write('</g>\n')

def write_svg(width, height, cpu_tenancy_by_pid, max_sample_count, tid_to_thread_name, process_id):
    writer = open('cpu-tenancy-{}.svg'.format(process_id), 'w')
    write_svg_header(writer, width, height)

    row_height = float((height - 60) / calculate_number_of_columns(cpu_tenancy_by_pid))
    unit_width = float((width - 40) / float(max_sample_count))

    colours = init_colours()

    y_offset = 50
    thread_name_to_tid = dict()
    for t in tid_to_thread_name:
        thread_name_to_tid[tid_to_thread_name[t]] = t
    for pid in sorted(cpu_tenancy_by_pid.iterkeys()):
        for tid in sorted(cpu_tenancy_by_pid[pid].iterkeys()):
            cpu_sample_count = cpu_tenancy_by_pid[pid][tid]
            x_offset = 20
            thread_name = "unknown/" + str(tid)
            if tid in tid_to_thread_name:
                thread_name = tid_to_thread_name[tid]
            for cpu_id in sorted(cpu_sample_count.iterkeys()):
                if cpu_id is not 'all':
                    percentage_of_total = 100 * float(cpu_sample_count[cpu_id] / float(cpu_sample_count['all']))
                    sample_width = unit_width * cpu_sample_count[cpu_id]

                    write_cell(writer, x_offset, y_offset, sample_width, row_height, cpu_id, thread_name, percentage_of_total, colours)
                    x_offset += sample_width
            overlay_thread_name(writer, 20, y_offset, thread_name)
            y_offset += row_height
                
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
    # TODO min height ~25
    process_id = sys.argv[1]
    tid_to_thread_name = get_tid_to_thread_name(sys.argv[2])
    cpu_tenancy_by_pid, max_sample_count = get_cpu_tenancy_count_by_tid()

    write_svg(1200, 660, cpu_tenancy_by_pid, max_sample_count, tid_to_thread_name, process_id)
