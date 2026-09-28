#!/bin/bash

for d in microbench/*/; do
  benchmark=`basename $d`
  echo -n $benchmark
  for ((i=0; i< (30 - ${#d}); i++)){ echo -n "-"; }
  cat $d/desc.txt
   
  build/X86/gem5.opt basic_OoO_microbench.py -b $benchmark

  mv m5out/stats.txt m5out/stats.$benchmark.txt
done


