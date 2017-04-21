#!/usr/bin/python

import json
import sys

STATE_COLOURS = {'S': '#acff90', 'R': '#ffaeae', 'D': '#fce94f', 'U': '#ccc'}
STROKE_COLOURS = {'S': '#679657', 'R': '#b07979', 'D': '#b3a639', 'U': '#aaa'}


def write_svg_header(writer, width, height):
    writer.write(
        '<?xml version="1.0" standalone="no"?>' +
        '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">')
    writer.write(
        '<svg version="1.1" width="' + str(width) + '" height="' + str(height) + '" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">\n')
    writer.write(
        '<text text-anchor="middle" x="{}" y="30" font-size="20" font-family="monospace" fill="#000">Thread scheduling states</text>'.format(width / 2))


def write_svg_footer(writer):
    writer.write('</svg>\n')


def calculate_number_of_columns(cpu_tenancy_by_pid):
    column_count = 0
    for pid in cpu_tenancy_by_pid:
        column_count += len(cpu_tenancy_by_pid[pid])
    return column_count


def get_fill(state):
    return STATE_COLOURS[state]


def get_stroke(state):
    return STROKE_COLOURS[state]


def write_cell(writer, x_offset, y_offset, width, height, state, thread_name, count, total, text_written):
    state_percentage = 100 * (count / float(total))
    cell_text = '{}/{} ({:.2f}%)'.format(thread_name, state, state_percentage)
    writer.write('<g><title>{}</title>'.format(cell_text))
    writer.write(
        '<rect x="{}" y="{}" width="{}" height="{}" style="fill: {}; stroke:{}">'.format(x_offset, y_offset, width, height, get_fill(state), get_stroke(state)))
    writer.write('</rect>\n')
    if not text_written:
        writer.write(
            '<text x="{}" y="{}" width="{}" font-size="12" font-family="monospace" fill="#000">{}</text>'.format(
                x_offset, y_offset + 12, width, cell_text))
    writer.write('</g>\n')


def write_svg(width, height, thread_scheduling, max_total, tid_to_thread_name, process_id):
    writer = open('scheduler-profile-{}.svg'.format(process_id), 'w')
    write_svg_header(writer, width, height)

    row_height = float((height - 60) / len(thread_scheduling))
    border = 10
    y_offset = 50
    for tid in sorted(thread_scheduling.iterkeys()):
        x_offset = border
        tid_sample_count = thread_scheduling[tid]['total']
        single_sample_width = float((width - (2 * border)) / float(thread_scheduling[tid]['total']))
        text_written = False
        for state in ['S', 'R', 'D', 'U']:
            sample_count = thread_scheduling[tid][state]

            if sample_count > 0:
                state_width = sample_count * single_sample_width
                write_cell(writer, x_offset, y_offset, state_width, row_height, state, tid_to_thread_name[tid],
                           sample_count, tid_sample_count, text_written)
                x_offset += state_width
                text_written = True
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
                tid_to_thread_name[str(decimal_tid)] = thread_name
            except IndexError:
                print "Failed to parse tid from line: " + line
    return tid_to_thread_name


def filter_scheduler_info(thread_scheduling_info, threads_to_include):
    max_total_value = 0
    filtered = dict()
    for k in thread_scheduling_info.iterkeys():
        if k in threads_to_include.keys():
            if thread_scheduling_info[k]["S"] != thread_scheduling_info[k]["total"] and thread_scheduling_info[k]["total"] != 0:
                filtered[k] = thread_scheduling_info[k]
                if filtered[k]['total'] > max_total_value:
                    max_total_value = filtered[k]['total']

    return (filtered, max_total_value)


if __name__ == "__main__":
    tid_to_thread_name = get_tid_to_thread_name(sys.argv[1])
    process_id = sys.argv[2]
    thread_scheduling = json.load(sys.stdin)
    filtered_scheduling, max_total = filter_scheduler_info(thread_scheduling, tid_to_thread_name)
    write_svg(1200, 660, filtered_scheduling, max_total, tid_to_thread_name, process_id)
