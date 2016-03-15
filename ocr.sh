#!/bin/bash

cd tiffs
for tiff in **/*.tiff; do
  mkdir -p "../txt/$(dirname $tiff)"
  tesseract "$tiff" "../txt/$(dirname $tiff)/$(basename $tiff .tiff)"
done
