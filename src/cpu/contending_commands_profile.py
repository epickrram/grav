#!/usr/bin/python

import json
import sys

COLOURS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]

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


def get_fill(counter):
    return COLOURS[counter % len(COLOURS)]


def write_cell(writer, x_offset, y_offset, width, height, command, count, total_count, counter):
    state_percentage = 100 * (count / float(total_count))
    cell_text = '{} ({:.2f}%)'.format(command, state_percentage)
    writer.write('<g><title>{}</title>'.format(cell_text))
    writer.write('<rect x="{}" y="{}" width="{}" height="{}" fill="{}">'.format(x_offset, y_offset, width, height, get_fill(counter)))
    writer.write('</rect>\n')
    writer.write('<text x="{}" y="{}" width="{}" font-size="12" font-family="monospace" style="text-overflow: clip" fill="#000">{}</text>'.format(x_offset, y_offset + 12, width, cell_text))
    writer.write('</g>\n')


def write_svg(width, height, ordered_commands, max_total, process_id):
    writer = open('contending-commands-{}.svg'.format(process_id), 'w')
    write_svg_header(writer, width, height)

    row_height = float(height / len(ordered_commands))
    single_sample_width = float(width / float(max_total))

    x_offset = 0
    counter = 0
    y_offset = 0
    for command_count in ordered_commands:
        sample_count = command_count["count"]
        if sample_count > 0:
            write_cell(writer, x_offset, y_offset, sample_count * single_sample_width, row_height, command_count["command"], sample_count, max_total, counter)
        y_offset += row_height
        counter += 1
    write_svg_footer(writer)
    writer.close()


def order_command_info(contending_commands):
    ordered_commands = []
    max_command_count = 0
    for k, v in contending_commands.iteritems():
        ordered_commands.append({"command": k, "count": v})
        if v > max_command_count:
            max_command_count = v

    ordered_commands.sort(key=lambda data: data["count"], reverse=True)
    return ordered_commands, max_command_count


if __name__ == "__main__":
    process_id = sys.argv[1]
    contending_commands = json.load(sys.stdin)
    ordered_commands, max_total = order_command_info(contending_commands)
    write_svg(1200, 600, ordered_commands, max_total, process_id)
