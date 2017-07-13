#!/usr/bin/python

import os
import re
import sys


def fillSamplesPerStack(stack, samples_list_by_stack):
    for key, value in samples_list_by_stack.items():
        if key in stack:
            value.append(int(stack[key]))
        else:
            value.append(0)
    return

def parseCollapsedLine(line, file_stacks, samples_list_by_stack):
    m = p.match(line)
    if m:
        key = m.group(1)
        value = m.group(2)
        file_stacks[key] = value
        samples_list_by_stack[key] = []

def createOutputFileName(collapsed_file_prefix):
    return "animated-%s.collapsed" % collapsed_file_prefix

def findCollapsedFiles(collapsed_files_dir):
    files = os.listdir(collapsed_files_dir)
    files = [os.path.join(collapsed_files_dir, f) for f in files]
    files.sort(key=os.path.getctime)
    collapsed_files = []
    for file in files:
        if os.path.basename(file).startswith(collapsed_file_prefix):
            collapsed_files.append(file)
    return collapsed_files

if __name__ == "__main__":
    argsLength = len(sys.argv)
    if (argsLength < 3 or argsLength > 4):
        print("Usage: %s <collapsed file prefix> (<output file>)" % (sys.argv[0]))
        sys.exit(1)

    collapsed_files_dir = sys.argv[1]
    collapsed_file_prefix = sys.argv[2]
    if argsLength == 3:
        output_file = createOutputFileName(collapsed_file_prefix)
    else:
        output_file = sys.argv[3]

    samples_list_by_stack = {}
    p = re.compile('(.*)\s+(\d+)')
    collapsed_files = findCollapsedFiles(collapsed_files_dir)
    stacks = []
    for f in collapsed_files:
        with open(f, "r") as ins:
            file_stacks = {}
            for line in ins:
                parseCollapsedLine(line, file_stacks, samples_list_by_stack)
            stacks.append(file_stacks)

    for stack in stacks:
        fillSamplesPerStack(stack, samples_list_by_stack)

    out = open(output_file, 'w')
    for key, value in samples_list_by_stack.items():
        samples = ' '.join(map(str,value))
        out.write("%s %s\n" % (key, samples))
    out.flush()
