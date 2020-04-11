#!/usr/bin/env bash

warc_file=warc/stopcoronavirus-russia."$(date +"%T")"

mkdir -p warc/

wget \
  -e robots=off \
  --span-hosts \
  --no-clobber \
  --page-requisites \
  --html-extension \
  --restrict-file-names=windows \
  --no-parent \
  --convert-links \
  https://стопкоронавирус.рф \
  --warc-file "$warc_file"
