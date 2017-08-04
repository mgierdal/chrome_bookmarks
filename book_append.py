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

__version__ = '0.9.1'

def dice_bookmarks(bookmarks_list):
    '''partitions a list of HTML lines
    into 3 components: head, bookmarks and tail.
    '''
    PT = r'(?P<head>.*?<DL><p>)(?P<bookmarks>.+)(?P<tail></DL>.*)'
    txt = ''.join(bookmarks_list)
    out = re.search(PT, txt, re.DOTALL).groups()
    print len(out[0]), len(out[1]), len(out[2])
    return out

if __name__ == "__main__":
    # setting CLI parser and parsing arguments
    parser = argparse.ArgumentParser(description='Deduplicate bookmark file')
    parser.add_argument("bmark_p", help="principal HTML file",
                        type=str)
    parser.add_argument("bmark_s", help="subsidiary HTML, to be inserted into the principal",
                        type=str)
    parser.add_argument('-o','--out', metavar='OUTPUT', help='output file')
    args = parser.parse_args()

    # ingesting input data
    print 'principal input file',
    princ_bm = open(args.bmark_p, 'r').readlines()
    print ' ... ingested'
    print 'XML size: {} lines'.format(len(princ_bm))
    princ_diced = dice_bookmarks(princ_bm)
    print 'subsidiary input file',
    sub_bm = open(args.bmark_s, 'r').readlines()
    print ' ... ingested'
    print 'XML size: {} lines'.format(len(sub_bm))
    sub_diced = dice_bookmarks(sub_bm)

    if args.out is None:
        fout = sys.stdout
    else:
        fout = open(args.out, 'w')
    fout.write(princ_diced[0])
    fout.write(princ_diced[1])
    fout.write(sub_diced[1])
    fout.write(princ_diced[2])
    fout.close()
