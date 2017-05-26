#!/bin/bash

MAX_PROCS=20

DIR=$(readlink -e $(dirname "${BASH_SOURCE[0]}")/..)
WIKI_SRC=$(readlink -e $DIR/../wiki)

is_ignore() {
    [ "$1" == '.ignore' ] || [ "$1" == 'README.org' ]
}

ls_files() {
    while read -r f; do
        if ! is_ignore $f; then
            echo $f
        fi
    done < <(git -C $WIKI_SRC ls-files)
}

gen_wiki_page() {
    echo pandoc --filter=$DIR/_scripts/wiki-pandoc.py \
           --template $DIR/_scripts/page.html \
           -o $DIR/"${1%.*}.html" \
           $WIKI_SRC/"$1"
}

cur=0
for f in $(ls_files); do
    mkdir -p $DIR/$(dirname $f)
    if [ ! -e "$f" ] || [ "$WIKI_SRC/$f" -nt "$DIR/$f" ]; then
        if [[ "$f" == *'.org' ]]; then
            gen_wiki_page $f &
        else
            echo cp $WIKI_SRC/$f $DIR/$f
        fi
        cur=$((cur+1))
    fi
    if [ "$MAX_PROCS" -gt 0 -a "$cur" -ne "$MAX_PROCS" ]; then
        wait
    fi
done

wait
