# coding: utf-8

import os
import sys
import bs4
#import lxml
import xml
#import json
from pprint import pprint
from collections import Counter
import re
from time import time
import argparse
#import xml.etree.ElementTree as ET


CURR_BMARK_FILE = r'C:\Users\mgier\AppData\Local\Google\Chrome\User Data\Default\Bookmarks'
#CURR_BMARK_FILE = r'C:\Users\mgier\Documents\code\chrome_bookmarks\Bookmarks'
#CURR_BMARK_FILE = r'C:\Users\mgier\Documents\code\chrome_bookmarks\Bookmarks.bak'
CURR_BMARK_FILE = r'C:\porta\PortableApps\GoogleChromePortable\Data\profile\Default\bookmarks_4_4_17.html'
#CURR_BMARK_FILE = r'C:\Users\mgier\AppData\Local\Google\Chrome\User Data\Default\bookmarks_4_6_17.html'
CURR_BMARK_FILE = r'bookmarks_2_10_17.html'
#CURR_BMARK_FILE = r'C:\Users\mgier\Documents\code\chrome_bookmarks\bookmarks_12_27_16.html'

print 'input file',
bm = open(CURR_BMARK_FILE, 'r').readlines()
print ' ... ingested'
print 'XML size: {} lines'.format(len(bm))
time_start = time()
print 'XML',
tree = bs4.BeautifulSoup(reduce(lambda x,y:x+y, bm), "lxml")
print ' ... parsed in {} sec'.format(time() - time_start)
print '{} sec per line'.format((time() - time_start)/len(bm))

#extract all URL entries, i.e. leaves whose keypath ends with 'url'
url_list =  [a.attrs['href'] for a in tree.find_all('a')[:]]
print '{} individual URLs'.format(len(url_list))

# sublist duplicated URLs, discounting administrative entries,
# i.e. containing 'chrome://' pseudo-URL 
url_counter = Counter(url_list)
duped_urls = [(k,v) for k,v in url_counter.iteritems()
              if (v>1) & (k.split(':')[0] != 'chrome')]
deletions = sum([v for k,v in duped_urls])
duped_urls = [k for k,v in duped_urls]
print '{} duplicated URLs'.format(len(duped_urls))
print '{} deletions required'.format(deletions)


time_decompose = time()
count = 0
for el in duped_urls[:100]:
    to_delete = tree.find_all(href=el)[1:]
    #print len(to_delete), el
    for unwanted in to_delete:
        unwanted.decompose()
        count = count + 1
print '{} deletions performed in {} sec'.format(count, time() - time_decompose)
print '{} sec per deletion'.format((time() - time_decompose)/count)


#extract all URL entries, i.e. leaves whose keypath ends with 'url'
url_list =  [a.attrs['href'] for a in tree.find_all('a')[:]]

# sublist duplicated URLs, discounting administrative entries, i.e. containing 'chrome://' pseudo-URL 
url_counter = Counter(url_list)
duped_urls = [k for k,v in url_counter.iteritems() if (v>1) & (k.split(':')[0] != 'chrome')]
print len(duped_urls)

deduped_fname = CURR_BMARK_FILE + '.deduped.html'
print deduped_fname
orig_rec_limit = sys.getrecursionlimit()
new_rec_limit = orig_rec_limit * 100
sys.setrecursionlimit(new_rec_limit)
print 'recursion limit changed from {} to {}'.format(orig_rec_limit, new_rec_limit)
html = tree.prettify("utf-8")
sys.setrecursionlimit(orig_rec_limit)
with open(deduped_fname, "wb") as file:
    file.write(html)

####################
#extract all URL entries, i.e. leaves whose keypath ends with 'url'
url_list = [a.attrs['href']
            for a in bs4.BeautifulSoup(
                reduce(lambda x,y:x+y, open(CURR_BMARK_FILE, 'r').readlines()), "lxml").find_all('a')[:]]
print '{} individual URLs'.format(len(url_list))

url_list_new = [a.attrs['href']
            for a in bs4.BeautifulSoup(
                reduce(lambda x,y:x+y, open(deduped_fname, 'r').readlines()), "lxml").find_all('a')[:]]
print '{} individual URLs'.format(len(url_list_new))

print 'individual URLs are the same: {}'.format(set(url_list) == set(url_list_new))

