#!/bin/bash
FILES=$(ls docs/new/vm/*-chapter.md)
PREV_SUM=""
while true; do
    CUR_SUM=$(stat -f "%m" $FILES | shasum -a 256)
    if [ "$CUR_SUM" == "$PREV_SUM" ]; then
        echo "STABLE"
        exit 0
    fi
    PREV_SUM=$CUR_SUM
    echo "Checking... not stable yet."
    sleep 60
done
