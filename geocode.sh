#!/bin/bash -e

print_header=1
for infile in txt/**/*.txt; do
  python geocode.py $print_header "$infile"
  print_header=0
done
