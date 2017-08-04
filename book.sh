#!/usr/bin/env sh

#for i in `find . -type f -regex \.\\/[A-Za-z0-9]*`
for i in `find . -name "bookmark*html"`
do
echo $i
xurl.sh $i | grep '' -c
uniqurl.sh $i | grep '' -c
python bookmarks_xml.py -l $i

ext="${i##.*}"
base="${i%.*}"
urlfile=$base"_urls.txt"
grep '' $urlfile -c
cat $urlfile | sort | uniq | grep '' -c
done
