#!/usr/bin/python

import codecs
import re
import sys
import unicodedata

java_primitives = {
    'Z' : 'java::boolean',
    'B' : 'java::byte',
    'S' : 'java::short',
    'I' : 'java::int',
    'J' : 'java::long',
    'F' : 'java::float',
    'D' : 'java::double',
    'C' : 'java::char',
}

def translateJavaPrimitiveArrays(java_trace):
    text = java_trace
    try:
        if java_trace[0] == '[':
            name = java_primitives.get(java_trace[1])
            if name:
                text = name + "[]"
            elif text[1] == 'L':
                text = java_trace[2:] + "[]"
        elif java_trace[0] == 'L':
            text = java_trace[1:]
    except IndexError as e:
        print "Failed to parse: " + java_trace + ": " + str(e)
    return text

class PerfMapEntry:
    addr = 0
    toaddr = 0
    entry = ""
    def __init__(self, addr, size, entry):
        self.addr = addr
        self.toaddr = addr + size
        self.entry = entry

    def is_in_range(self, mapped_addr):
        return self.addr <= mapped_addr <= self.toaddr


def create_address_map(perf_agent_map_file):
    result_map = {}
    with open(perf_agent_map_file, "r") as ins:
        for line in ins:
            # 7f650d00045f e8 call_stub
            p = re.compile('(\w+)\s+(\w+)\s+(.*)')
            m = p.match(line)
            if m:
                addr = int(m.group(1), 16)
                size = int(m.group(2), 16)
                text = translateJavaPrimitiveArrays(m.group(3))
                entry = PerfMapEntry(addr, size, text)
                key = addr / aggregate_factor
                result_map.setdefault(key, []).append(entry)
    return result_map

def find_address_entry(addr, addresses):
    key = addr / aggregate_factor
    if key in addresses.keys():
        for map_entry in addresses[key]:
            if map_entry.is_in_range(addr):
                return map_entry
    return None

def map_addresses(line, addresses):
    p = re.findall(';0x([0-9a-f]+)', line)
    for match in p:
        addr = int(match, 16)
        matched_entry = find_address_entry(addr, addresses)
        if matched_entry:
            line = line.replace("0x" + match, matched_entry.entry)
        else:
            line = line.replace("0x" + match, "[unknown]")
    return line

def remove_control_characters(l):
    return "".join(ch for ch in l if unicodedata.category(ch)[0]!="C")

def tidy(line):
    allocated = line[:line.find(';')]
    line = line.replace(allocated, translateJavaPrimitiveArrays(allocated))
    line = re.sub(r'\(.*?\)', '', line)
    line = re.sub(r'\[clone.*?\]', '', line)
    line = remove_control_characters(line)
    return line

if __name__ == "__main__":
    aggregate_factor = 100000
    addresses = {}
    if (len(sys.argv) >  1):
        addresses = create_address_map(sys.argv[1])

    for line in codecs.getreader('utf-8')(sys.stdin):
        print tidy(map_addresses(line, addresses))

