#!/usr/bin/env bash

mkdir -p warc/
cd warc/ || exit

warc_file=stopcoronavirus-russia."$(date +"%s")"

wget \
  --delete-after --no-directories \
  -e robots=off \
  --span-hosts \
  --no-clobber \
  --page-requisites \
  --html-extension \
  --restrict-file-names=windows \
  --no-parent \
  --convert-links \
  https://стопкоронавирус.рф/information \
  --warc-file "$warc_file"

ipwb index "$warc_file.warc.gz" > "$warc_file.cdxj"

index_file_hash=$(ipfs add -Q "$warc_file.cdxj")

echo "Stored to IPFS as: $index_file_hash"

python ../run.py "$index_file_hash"
