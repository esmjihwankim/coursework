import math

perf_gains = []
with open("base_cycles.txt","r") as base_f:
  for line in base_f:
    benchmark,base_cycles = line.split()
    
    with open("m5out/stats."+benchmark+".txt","r") as f:
      for line in f:     
        if line.startswith("system.cpu.numCycles "):
          new_cycles = line.split()[1]
          # print(benchmark,base_cycles,new_cycles)
          perf_gain = float(base_cycles)/float(new_cycles)
          print(benchmark+" is improved by "+str(perf_gain)+"x")
          perf_gains.append(perf_gain)

def geomean(xs):
    return math.exp(math.fsum(math.log(x) for x in xs) / len(xs))

print("Geomean: " + str(geomean(perf_gains)) +"x")
          

      