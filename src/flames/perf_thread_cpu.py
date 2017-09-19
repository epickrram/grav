#!/usr/bin/python

import re
import sys

def get_thread_cpu_counts_from_perf_sample():
    cpu_count_by_thread = dict()
    process_name_by_tid = dict()
    max_cpu_id = 0
    for line in sys.stdin:
        #    esets_daemon  1514 [001]    86.411643
        try:
            tokens = re.split("\s+", line.strip())
            process_name = tokens[0].strip()
            tid = int(tokens[1].strip())

            if process_name not in process_name_by_tid:
                process_name_by_tid[tid] = process_name

            if tid not in cpu_count_by_thread:
                cpu_count_by_thread[tid] = dict()
            
            thread_cpu_counts = cpu_count_by_thread[tid]
            cpu_id = int(tokens[2].strip().replace("[", "").replace("]", ""))
            if cpu_id not in thread_cpu_counts:
                thread_cpu_counts[cpu_id] = 0
            thread_cpu_counts[cpu_id] += 1

            if cpu_id > max_cpu_id:
                max_cpu_id = cpu_id

        except (ValueError, IndexError):
            print("Failed to parse line: " + line)

    return (cpu_count_by_thread, process_name_by_tid, max_cpu_id)



if __name__ == "__main__":
    thread_cpu_counts, process_name_by_tid, max_cpu_id = get_thread_cpu_counts_from_perf_sample()
    current_cpu_id = 0
    tid_counts = dict()
    while current_cpu_id <= max_cpu_id:
        tid_counts[current_cpu_id] = dict()
        current_cpu_id += 1
    for tid in thread_cpu_counts:
        for cpu in thread_cpu_counts[tid]:
            if tid not in tid_counts[cpu]:
                tid_counts[cpu][tid] = dict()
            tid_counts[cpu][tid] = thread_cpu_counts[tid][cpu]

    for cpu in tid_counts:
        max_count = -1
        for tid in sorted(tid_counts[cpu], key=tid_counts[cpu].get, reverse=True):
            if max_count < 0:
                max_count = tid_counts[cpu][tid]
                
        current_count = 0
        while current_count <= max_count:
            data = str(cpu)
            for tid in sorted(tid_counts[cpu], key=tid_counts[cpu].get, reverse=True):
                # todo map tid to java thread name
                proc_name = process_name_by_tid[tid]
                if tid_counts[cpu][tid] >= current_count:
                    data += ";" + str(tid )

            data += " 1"
            print(data)
            current_count += 1

        
# cpu;tid count
# tid/proc;cpu_id count
#    for tid in thread_cpu_counts:
#        #data = str(tid) + "/" + process_name_by_tid[tid] + ";"
#        current_cpu_id = 0
#        while current_cpu_id <= max_cpu_id:
#            data = str(current_cpu_id) + ";" + process_name_by_tid[tid] + " "
#            count = 0
#            if current_cpu_id in thread_cpu_counts[tid]:
#                count = thread_cpu_counts[tid][current_cpu_id]
#            print(data + str(count))
#            current_cpu_id += 1


#    for tid in thread_cpu_counts:
#        data = "'" + process_name_by_tid[tid] + "' "
#        current_cpu_id = 0
#        while current_cpu_id <= max_cpu_id:
#            count = 0
#            if current_cpu_id in thread_cpu_counts[tid]:
#                count = thread_cpu_counts[tid][current_cpu_id]
#            data += str(count) + " "
#            current_cpu_id += 1
#
#        print(data)

