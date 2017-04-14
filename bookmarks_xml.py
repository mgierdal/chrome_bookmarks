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
import datetime
#import xml.etree.ElementTree as ET

__version__ = '0.9'

parser = argparse.ArgumentParser(description='Deduplicate bookmark file')
parser.add_argument("bmark_in", help="HTML file to be deduplicated",
                    type=str)
parser.add_argument("--ndel", help="delete first N duplicated URLs",
                    type=int)
parser.add_argument("--verify", help="verify that no URL was lost",
                    action="store_true")
args = parser.parse_args()

print 'input file',
bm = open(args.bmark_in, 'r').readlines()
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

if args.ndel:
    N = args.ndel
else:
    N = len(duped_urls)
print 'deduplicating {} URLs'.format(N)
for el in duped_urls[:N]:
    to_delete = tree.find_all(href=el)[1:]
    #print len(to_delete), el
    for unwanted in to_delete:
        unwanted.decompose()
        count = count + 1
time_spent = time() - time_decompose
print '{} deletions performed in {} sec'.format(count, time_spent)
print '{} sec per deletion'.format(time_spent/count)
print 'EPT of {} deletions: {} '.format(deletions, datetime.timedelta(seconds=(time_spent/count) * deletions))

#extract all URL entries, i.e. leaves whose keypath ends with 'url'
url_list =  [a.attrs['href'] for a in tree.find_all('a')[:]]

# sublist duplicated URLs, discounting administrative entries, i.e. containing 'chrome://' pseudo-URL 
url_counter = Counter(url_list)
duped_urls = [k for k,v in url_counter.iteritems() if (v>1) & (k.split(':')[0] != 'chrome')]
print '{} duplicated URLs'.format(len(duped_urls))

bmark_out = args.bmark_in + '.deduped.html'
print 'output: {}'.format(bmark_out)
orig_rec_limit = sys.getrecursionlimit()
new_rec_limit = orig_rec_limit * 100
print 'recursion limit changed from {} to {}'.format(orig_rec_limit, new_rec_limit)
sys.setrecursionlimit(new_rec_limit)
html = tree.prettify("utf-8")
sys.setrecursionlimit(orig_rec_limit)
print 'recursion limit changed from {} to {}'.format(new_rec_limit, orig_rec_limit)
with open(bmark_out, "wb") as file:
    file.write(html)
	print '{} SAVED'.format(os.path.basename(bmark_out))

####################
if args.verify:
    #extract all URL entries, i.e. leaves whose keypath ends with 'url'
    url_list = [a.attrs['href']
                for a in bs4.BeautifulSoup(
                    reduce(lambda x,y:x+y, open(args.bmark_in, 'r').readlines()), "lxml").find_all('a')[:]]
    print '{} individual URLs'.format(len(url_list))
    url_list_new = [a.attrs['href']
                for a in bs4.BeautifulSoup(
                    reduce(lambda x,y:x+y, open(bmark_out, 'r').readlines()), "lxml").find_all('a')[:]]
    print '{} individual URLs'.format(len(url_list_new))
    print 'individual URLs are the same: {}'.format(set(url_list) == set(url_list_new))

