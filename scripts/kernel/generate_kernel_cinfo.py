#! /usr/bin/env python2.6
# -*- mode: python; coding: utf-8; -*-
#
#  Codezero -- a microkernel for embedded systems.
#
#  Copyright © 2009  B Labs Ltd
#
import os, sys, shelve, glob
from os.path import join

PROJRELROOT = '../..'

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), PROJRELROOT)))
sys.path.append(os.path.abspath("../"))

from config.projpaths import *
from config.configuration import *


cinfo_file_start = \
'''/*
 * Autogenerated container descriptions
 * defined for the current build.
 *
 * Copyright (C) 2009 Bahadir Balban
 */
#include <l4/generic/container.h>
#include <l4/generic/resource.h>
#include <l4/generic/capability.h>
#include <l4/generic/cap-types.h>

%s

/*
 * FIXME:
 * Add irqs, exceptions
 */

struct container_info cinfo[] = {
'''
cinfo_file_end = \
'''
};
'''

cinfo_start = \
'''
\t[%d] = {
\t.name = "%s",
\t.npagers = 1,
\t.pager = {
'''

cinfo_end = \
'''
\t\t},
\t},
'''

pager_start = \
'''
\t\t[0] = {
\t\t\t.start_address = (CONFIG_CONT%(cn)d_START_PC_ADDR),
\t\t\t.pager_lma = __pfn(CONFIG_CONT%(cn)d_PAGER_LMA),
\t\t\t.pager_vma = __pfn(CONFIG_CONT%(cn)d_PAGER_VMA),
\t\t\t.pager_size = __pfn(page_align_up(CONFIG_CONT%(cn)d_PAGER_MAPSIZE)),
\t\t\t.ncaps = %(caps)d,
\t\t\t.caps = {
'''
pager_end = \
'''
\t\t\t},
\t\t},
'''

cap_virtmem = \
'''
\t\t\t[%(capidx)d] = {
\t\t\t\t.type = CAP_TYPE_MAP | CAP_RTYPE_VIRTMEM,
\t\t\t\t.access = CAP_MAP_READ | CAP_MAP_WRITE | CAP_MAP_EXEC
\t\t\t\t\t| CAP_MAP_CACHED | CAP_MAP_UNCACHED | CAP_MAP_UNMAP | CAP_MAP_UTCB,
\t\t\t\t.start = __pfn(CONFIG_CONT%(cn)d_VIRT%(vn)d_START),
\t\t\t\t.end = __pfn(CONFIG_CONT%(cn)d_VIRT%(vn)d_END),
\t\t\t\t.size = __pfn(CONFIG_CONT%(cn)d_VIRT%(vn)d_END - CONFIG_CONT%(cn)d_VIRT%(vn)d_START),
\t\t\t},
'''

cap_physmem = \
'''
\t\t\t[%(capidx)d] = {
\t\t\t\t.type = CAP_TYPE_MAP | CAP_RTYPE_PHYSMEM,
\t\t\t\t.access = CAP_MAP_READ | CAP_MAP_WRITE | CAP_MAP_EXEC |
\t\t\t\t\tCAP_MAP_CACHED | CAP_MAP_UNCACHED | CAP_MAP_UNMAP | CAP_MAP_UTCB,
\t\t\t\t.start = __pfn(CONFIG_CONT%(cn)d_PHYS%(pn)d_START),
\t\t\t\t.end = __pfn(CONFIG_CONT%(cn)d_PHYS%(pn)d_END),
\t\t\t\t.size = __pfn(CONFIG_CONT%(cn)d_PHYS%(pn)d_END - CONFIG_CONT%(cn)d_PHYS%(pn)d_START),
\t\t\t},
'''

cap_all_others = \
'''
\t\t\t[%d] = {
\t\t\t\t.type = CAP_TYPE_IPC | CAP_RTYPE_CONTAINER,
\t\t\t\t.access = CAP_IPC_SEND | CAP_IPC_RECV
\t\t\t\t          | CAP_IPC_FULL | CAP_IPC_SHORT
\t\t\t\t          | CAP_IPC_EXTENDED,
\t\t\t\t.start = 0, .end = 0, .size = 0,
\t\t\t},
\t\t\t[%d] = {
\t\t\t\t.type = CAP_TYPE_TCTRL | CAP_RTYPE_CONTAINER,
\t\t\t\t.access = CAP_TCTRL_CREATE | CAP_TCTRL_DESTROY
\t\t\t\t          | CAP_TCTRL_SUSPEND | CAP_TCTRL_RUN
\t\t\t\t          | CAP_TCTRL_RECYCLE | CAP_TCTRL_WAIT,
\t\t\t\t.start = 0, .end = 0, .size = 0,
\t\t\t},
\t\t\t[%d] = {
\t\t\t\t.type = CAP_TYPE_EXREGS | CAP_RTYPE_CONTAINER,
\t\t\t\t.access = CAP_EXREGS_RW_PAGER
\t\t\t\t          | CAP_EXREGS_RW_UTCB | CAP_EXREGS_RW_SP
\t\t\t\t          | CAP_EXREGS_RW_PC | CAP_EXREGS_RW_REGS,
\t\t\t\t.start = 0, .end = 0, .size = 0,
\t\t\t},
\t\t\t[%d] = {
\t\t\t\t.type = CAP_TYPE_CAP | CAP_RTYPE_CONTAINER,
\t\t\t\t.access = CAP_CAP_MODIFY | CAP_CAP_GRANT
\t\t\t\t| CAP_CAP_READ | CAP_CAP_SHARE,
\t\t\t\t.start = 0, .end = 0, .size = 0,
\t\t\t},
\t\t\t[%d] = {
\t\t\t\t.type = CAP_TYPE_UMUTEX | CAP_RTYPE_CONTAINER,
\t\t\t\t.access = CAP_UMUTEX_LOCK | CAP_UMUTEX_UNLOCK,
\t\t\t\t.start = 0, .end = 0, .size = 0,
\t\t\t},
\t\t\t[%d] = {
\t\t\t\t.type = CAP_TYPE_QUANTITY
\t\t\t\t	  | CAP_RTYPE_THREADPOOL,
\t\t\t\t.access = 0, .start = 0, .end = 0,
\t\t\t\t.size = 64,
\t\t\t},
\t\t\t[%d] = {
\t\t\t\t.type = CAP_TYPE_QUANTITY | CAP_RTYPE_SPACEPOOL,
\t\t\t\t.access = 0, .start = 0, .end = 0,
\t\t\t\t.size = 64,
\t\t\t},
\t\t\t[%d] = {
\t\t\t\t.type = CAP_TYPE_QUANTITY | CAP_RTYPE_CPUPOOL,
\t\t\t\t.access = 0, .start = 0, .end = 0,
\t\t\t\t.size = 50,	/* Percentage */
\t\t\t},
\t\t\t[%d] = {
\t\t\t\t.type = CAP_TYPE_QUANTITY | CAP_RTYPE_MUTEXPOOL,
\t\t\t\t.access = 0, .start = 0, .end = 0,
\t\t\t\t.size = 100,
\t\t\t},
\t\t\t[%d] = {
\t\t\t\t/* For pmd accounting */
\t\t\t\t.type = CAP_TYPE_QUANTITY | CAP_RTYPE_MAPPOOL,
\t\t\t\t.access = 0, .start = 0, .end = 0,
\t\t\t\t/* Function of mem regions, nthreads etc. */
\t\t\t\t.size = (64 * 30 + 100),
\t\t\t},
\t\t\t[%d] = {
\t\t\t\t/* For cap spliting, creating, etc. */
\t\t\t\t.type = CAP_TYPE_QUANTITY | CAP_RTYPE_CAPPOOL,
\t\t\t\t.access = 0, .start = 0, .end = 0,
\t\t\t\t/* This may be existing caps X 2 etc. */
\t\t\t\t.size = 30,
\t\t\t},
'''

pager_ifdefs_todotext = \
'''
/*
 * TODO:
 * This had to be defined this way because in CML2 there
 * is no straightforward way to derive symbols from expressions, even
 * it is stated in the manual that it can be done.
 * As a workaround, a ternary expression of (? : ) was tried but this
 * complains that type deduction could not be done.
 */'''

# This will be filled after the containers are compiled
# and pager binaries are formed
pager_mapsize = \
'''
#define CONFIG_CONT%d_PAGER_SIZE     %s
'''

pager_ifdefs = \
'''
#if defined(CONFIG_CONT%(cn)d_TYPE_LINUX)
    #define CONFIG_CONT%(cn)d_START_PC_ADDR \\
        (CONFIG_CONT%(cn)d_LINUX_ZRELADDR - CONFIG_CONT%(cn)d_LINUX_PHYS_OFFSET + \\
         CONFIG_CONT%(cn)d_LINUX_PAGE_OFFSET)
    #define CONFIG_CONT%(cn)d_PAGER_LMA  (CONFIG_CONT%(cn)d_LINUX_PHYS_OFFSET)
    #define CONFIG_CONT%(cn)d_PAGER_VMA  (CONFIG_CONT%(cn)d_LINUX_PAGE_OFFSET)
    #define CONFIG_CONT%(cn)d_PAGER_MAPSIZE \\
                (CONFIG_CONT%(cn)d_PAGER_SIZE + CONFIG_CONT%(cn)d_LINUX_ZRELADDR - \\
                 CONFIG_CONT%(cn)d_LINUX_PHYS_OFFSET)
#else
    #define CONFIG_CONT%(cn)d_START_PC_ADDR (CONFIG_CONT%(cn)d_PAGER_VMA)
    #define CONFIG_CONT%(cn)d_PAGER_MAPSIZE (CONFIG_CONT%(cn)d_PAGER_SIZE)
#endif
'''
def generate_pager_memory_ifdefs(config, containers):
    pager_ifdef_string = ""
    linux = 0
    for c in containers:
        if c.type == "linux":
            if linux == 0:
                pager_ifdef_string += pager_ifdefs_todotext
                linux = 1
        pager_ifdef_string += \
            pager_mapsize % (c.id, config.containers[c.id].pager_size)
        pager_ifdef_string += pager_ifdefs % { 'cn' : c.id }
    return pager_ifdef_string

def generate_kernel_cinfo(config, cinfo_path):
    containers = config.containers
    containers.sort()

    print "Generating kernel cinfo..."
    #config.config_print()

    pager_ifdefs = generate_pager_memory_ifdefs(config, containers)

    with open(cinfo_path, 'w+') as cinfo_file:
        fbody = cinfo_file_start % pager_ifdefs
        total_other_caps = 11
        for c in containers:
            # Currently only these are considered as capabilities
            total_caps = c.virt_regions + c.phys_regions + total_other_caps
            fbody += cinfo_start % (c.id, c.name)
            fbody += pager_start % { 'cn' : c.id, 'caps' : total_caps}
            cap_index = 0
            for mem_index in range(c.virt_regions):
                fbody += cap_virtmem % { 'capidx' : cap_index, 'cn' : c.id, 'vn' : mem_index }
                cap_index += 1
            for mem_index in range(c.phys_regions):
                fbody += cap_physmem % { 'capidx' : cap_index, 'cn' : c.id, 'pn' : mem_index }
                cap_index += 1
            fbody += cap_all_others % tuple(range(cap_index, total_caps))
            fbody += pager_end
            fbody += cinfo_end
        fbody += cinfo_file_end
        cinfo_file.write(fbody)

if __name__ == "__main__":
    config = configuration_retrieve()
    if len(sys.argv) > 1:
        generate_kernel_cinfo(config, join(PROJROOT, sys.argv[1]))
    else:
        generate_kernel_cinfo(config, join(PROJROOT, 'src/generic/cinfo.c'))

