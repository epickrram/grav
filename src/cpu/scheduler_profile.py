#!/usr/bin/python

import json
import sys

STATE_COLOURS = {'S': '#0c0', 'R': '#900', 'D': '#FCE94F', 'U': '#ccc'}

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


def get_fill(state):
    return STATE_COLOURS[state]


def write_cell(writer, x_offset, y_offset, width, height, state, thread_name, count, total):
    state_percentage = 100 * (count / float(total))
    cell_text = '{}/{} ({:.2f}%)'.format(thread_name, state, state_percentage)
    writer.write('<g><title>{}</title>'.format(cell_text))
    writer.write('<rect x="{}" y="{}" width="{}" height="{}" fill="{}">'.format(x_offset, y_offset, width, height, get_fill(state)))
    writer.write('</rect>\n')
    writer.write('<text x="{}" y="{}" width="{}" font-size="12" font-family="monospace" style="text-overflow: clip" fill="#000">{}</text>'.format(x_offset, y_offset + 12, width, cell_text))
    writer.write('</g>\n')


def write_svg(width, height, thread_scheduling, max_total, tid_to_thread_name, process_id):
    writer = open('scheduler-profile-{}.svg'.format(process_id), 'w')
    write_svg_header(writer, width, height)

    column_width = float(width / len(thread_scheduling))
    single_sample_height = float(height / float(max_total))

    x_offset = 0
    for tid in sorted(thread_scheduling.iterkeys()):
        y_offset = height
        tid_sample_count = thread_scheduling[tid]['total']
        if tid_sample_count > 0:
            single_sample_height = float(height / float(thread_scheduling[tid]['total']))
            for state in ['S', 'R', 'D', 'U']:
                sample_count = thread_scheduling[tid][state]
                if sample_count > 0:
                    state_height = sample_count * single_sample_height
                    write_cell(writer, x_offset, y_offset - state_height, column_width, state_height, state, tid_to_thread_name[tid], sample_count, tid_sample_count)
                    y_offset -= state_height
            x_offset += column_width
        else:
            print "{}: {}".format(tid, thread_scheduling[tid])

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
                tid_to_thread_name[str(decimal_tid)] = thread_name
            except IndexError:
                print "Failed to parse tid from line: " + line
    return tid_to_thread_name


def filter_scheduler_info(thread_scheduling_info, threads_to_include):
    max_total_value = 0
    filtered = dict()
    for k in thread_scheduling_info.iterkeys():
        if k in threads_to_include.keys():
            filtered[k] = thread_scheduling_info[k]
            if filtered[k]['total'] > max_total_value:
                max_total_value = filtered[k]['total']

    return (filtered, max_total_value)


if __name__ == "__main__":
    tid_to_thread_name = get_tid_to_thread_name(sys.argv[1])
    process_id = sys.argv[2]
    thread_scheduling = json.load(sys.stdin)
    filtered_scheduling, max_total = filter_scheduler_info(thread_scheduling, tid_to_thread_name)
    write_svg(1200, 600, filtered_scheduling, max_total, tid_to_thread_name, process_id)
