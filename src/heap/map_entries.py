#!/usr/bin/python

import re
import sys


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


def create_address_map():
    result_map = {}
    with open(perf_agent_map_file, "r") as ins:
        for line in ins:
            # 7f650d00045f e8 call_stub
            p = re.compile('(\w+)\s+(\w+)\s+(.*)')
            m = p.match(line)
            if m:
                addr = int(m.group(1), 16)
                size = int(m.group(2), 16)
                entry = PerfMapEntry(addr, size, m.group(3))
                key = addr / aggregate_factor
                result_map.setdefault(key, []).append(entry)
    return result_map

def find_address_entry(addr):
    key = addr / aggregate_factor
    if key in addresses.keys():
        for map_entry in addresses[key]:
            if map_entry.is_in_range(addr):
                return map_entry
    return None

if __name__ == "__main__":
    perf_agent_map_file = sys.argv[1]
    heap_file = sys.argv[2]

    aggregate_factor = 100000
    addresses = create_address_map()

    with open(heap_file, "r") as ins:
        for line in ins:
            # (from raw 7f6522890fdf     )
            p = re.compile('(.*)\(from\s+raw\s+(\w+)\s+\)')
            m = p.match(line)
            if m:
                prefix = m.group(1)
                addr = int(m.group(2), 16)
                matched_entry = find_address_entry(addr)
                if matched_entry:
                    print "%s (addr = %s) matches %s" % (prefix, hex(addr), matched_entry.entry)
                else:
                    print "%s (addr = %s) NO_MATCH_IN_MAP" % (prefix, addr)
            else:
                print "%s NOT_FOUND" % line.rstrip()