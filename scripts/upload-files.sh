#!/bin/bash

BUCKET_NAME="file-upload-bucket-ngt-file-processor"
NUM_FILES=20
MAX_CONCURRENT=5

mkdir -p test_files
for i in $(seq 1 $NUM_FILES); do
    echo "Test content for file $i" > "test_files/file$i.txt"
done

upload_file() {
    local file=$1
    local target="gs://$BUCKET_NAME/$(basename $file)"
    echo "Uploading $file to $target..."
    gsutil cp "$file" "$target"
    echo "Finished uploading $file"
}

pids=()
count=0

for file in test_files/*; do
    upload_file "$file" &
    pids+=($!)
    count=$((count + 1))
    
    if [ $count -ge $MAX_CONCURRENT ]; then
        wait ${pids[0]}
        pids=("${pids[@]:1}")
        count=$((count - 1))
    fi
done

for pid in "${pids[@]}"; do
    wait $pid
done

echo "All uploads completed!"