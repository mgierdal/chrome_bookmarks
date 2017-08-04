#!/usr/bin/env sh

#for i in `find . -type f -regex \.\\/[A-Za-z0-9]*`
for i in `find . -name "bookmark*html"`
do
echo $i
#name parsing
ext="${i##.*}"
base="${i%.*}"
#extracting URLs
allurlfile=$base"_all_urls.txt"
xurl.sh $i > $allurlfile
echo "all_extracted:" $(cat $allurlfile | grep '' -c)
#unique URLs
uniqurlsfile=$base"_uniq_urls.txt"
uniqurl.sh $i > $uniqurlsfile
echo "uniq_urls:" $(cat $uniqurlsfile | grep '' -c)

python bookmarks_xml.py -l $i

urlfile=$base"_urls.txt"
echo "all_output:" $(grep '' $urlfile -c)
echo "uniq_output:" $(cat $urlfile | sort | uniq | grep '' -c)
done
