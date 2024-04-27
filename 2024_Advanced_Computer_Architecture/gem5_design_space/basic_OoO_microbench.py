# -*- coding: utf-8 -*-
# Copyright (c) 2015 Jason Power
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met: redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer;
# redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution;
# neither the name of the copyright holders nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


import argparse

# import the m5 (gem5) library created when gem5 is built
import m5

# import all of the SimObjects
from m5.objects import *


parser = argparse.ArgumentParser()
parser.add_argument("-b", "--benchmark", default = "MIP")

args = parser.parse_args()

thispath = os.path.dirname(os.path.realpath(__file__))
binary = os.path.join(thispath, 'microbench', args.benchmark, 'bench.X86')



# create the system we are going to simulate
system = System()

# Set the clock fequency of the system (and all of its children)
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()

# Set up the system
system.mem_mode = 'timing'               # Use timing accesses
system.mem_ranges = [AddrRange('8192MB')] # Create an address range


class L1CacheLatency(Cache):
    tag_latency = 2
    data_latency = 2
    response_latency = 2
    tgts_per_mshr = 20

class L2CacheLatency(Cache):
    tag_latency = 20
    data_latency = 20
    response_latency = 20
    tgts_per_mshr = 12

##########################################
## Modify only the values below +++
##########################################

class myO3CPU(O3CPU):
    # None
    fetchWidth = 8 # Fetch width (need to be set to a value between 8-12)
    fetchBufferSize = 32 # Fetch buffer size in bytes
    fetchQueueSize = 16 # Fetch queue size in micro-ops per-thread
    decodeWidth = 2 # Decode width (max 12)
    renameWidth = 2 # Rename width (max 12)
    dispatchWidth = 2 # Dispatch width (max 12)
    issueWidth = 2 # Issue width (max 12)
    wbWidth = 2 # Writeback width
    commitWidth = 2 # Commit width (max 12)
    squashWidth = 2 # Squash width    
    LQEntries = 16 # Number of load queue entries
    SQEntries = 16 # Number of store queue entries
    numPhysIntRegs = 64 # Number of physical integer registers
    numPhysFloatRegs = 64 # Number of physical floating point registers
    numIQEntries = 32 # Number of instruction queue entries
    numROBEntries = 64 # Number of reorder buffer entries
    
    _cost=fetchWidth*fetchBufferSize*fetchQueueSize*decodeWidth*renameWidth*dispatchWidth*issueWidth*wbWidth*commitWidth*squashWidth*LQEntries*SQEntries*numPhysIntRegs*numPhysFloatRegs*numIQEntries*numROBEntries

class L1ICache(L1CacheLatency):
    _size_inKB = 8
    assoc = 2
    mshrs = 2     
    
    size = str(_size_inKB) + 'kB' 

    _cost=_size_inKB*assoc*mshrs

class L1DCache(L1CacheLatency):
    _size_inKB = 8
    assoc = 2
    mshrs = 2      
    
    size = str(_size_inKB) + 'kB'
    
    _cost=_size_inKB*assoc*mshrs

class L2Cache(L2CacheLatency):
    _size_inKB = 32
    assoc = 8
    mshrs = 8
    
    size = str(_size_inKB) + 'kB'

    _cost=_size_inKB*assoc*mshrs

##########################################
## Modify only the values above ---
##########################################


# Create a simple CPU
system.cpu = myO3CPU()

system.cpu.icache = L1ICache()
system.cpu.dcache = L1DCache()
system.cpu.l2cache = L2Cache()

total_cost = system.cpu._cost * system.cpu.icache._cost * system.cpu.dcache._cost * system.cpu.l2cache._cost 
base_cost = 2361183241434822606848
budget = 2**16
print("total_cost:", total_cost)
if(total_cost > base_cost * budget): print("cost exedeed the limit!")


# Create a memory bus, a system crossbar, in this case
system.membus = SystemXBar()
system.l2bus = L2XBar()

system.cpu.icache.cpu_side = system.cpu.icache_port
system.cpu.dcache.cpu_side = system.cpu.dcache_port

system.cpu.icache.mem_side  = system.l2bus.cpu_side_ports
system.cpu.dcache.mem_side  = system.l2bus.cpu_side_ports

system.cpu.l2cache.cpu_side = system.l2bus.mem_side_ports
system.cpu.l2cache.mem_side  = system.membus.cpu_side_ports



# create the interrupt controller for the CPU and connect to the membus
system.cpu.createInterruptController()

# For x86 only, make sure the interrupts are connected to the memory
# Note: these are directly connected to the memory bus and are not cached
if m5.defines.buildEnv['TARGET_ISA'] == "x86":
    system.cpu.interrupts[0].pio = system.membus.mem_side_ports
    system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
    system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

# Create a DDR3 memory controller and connect it to the membus
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

# Connect the system up to the membus
system.system_port = system.membus.cpu_side_ports

# get ISA for the binary to run.
isa = str(m5.defines.buildEnv['TARGET_ISA']).lower()

system.workload = SEWorkload.init_compatible(binary)

# Create a process for a simple "Hello World" application
process = Process()
# Set the command
# cmd is a list which begins with the executable (like argv)
process.cmd = [binary]
# Set the cpu to use the process as its workload and create thread contexts
system.cpu.workload = process
system.cpu.createThreads()

# set up the root SimObject and start the simulation
root = Root(full_system = False, system = system)
# instantiate all of the objects we've created above
m5.instantiate()

print("Beginning simulation!")
exit_event = m5.simulate()
print('Exiting @ tick %i because %s' % (m5.curTick(), exit_event.getCause()))
