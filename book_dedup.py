#!/usr/bin/env python

# coding: utf-8

import os, sys
from pprint import pprint
import re
from collections import Counter 
from itertools import tee, izip
import argparse

__version__ = "1.9.7"

PTRN = r'<DT><A HREF="(.+?://.+?)"'
EMPTY_LINE = '\n'
#EMPTY_LINE = '*****\n'

def get_url_counter(bookmark_file_list, duped=False):
    '''duped - if True, only multiplicated URLs are counted (default=False)'''
    urls = [x[0] for x in [re.findall(PTRN, x) for x in bookmark_file_list] if x != []]
    url_counter = Counter(urls)
    if duped:
        return Counter({k:v for k,v in list(url_counter.iteritems()) if v > 1})
    else:
        return url_counter
    
def first_bookmark_filter(entry, url_counter, ptrn):
    '''TODO'''
    bookmark = re.search(ptrn, entry)
    if bookmark:
        url = bookmark.group(1)
        if url_counter[url] > 0: 
            del url_counter[url]
            return True
        else:
            return False
    else:
        return True

def pairwise(iterable):
    '''s -> (s0,s1), (s1,s2), (s2, s3), ...'''
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)

def delete_empty_folders_chrome(bookmarks, verbose=False):
    '''TODO'''
    indices = [i for i,v in enumerate(pairwise([x.strip() for x in bookmarks
                                                if x.strip() > ''])) 
               if ''.join(v) == '<DL><p></DL><p>']

    for ix in indices:
        if verbose:
            print 'CH at index {} - folder {}, empty body {} {} '\
                  .format(ix,
                          bookmarks[ix-1].strip(),
                          bookmarks[ix+0].strip(),
                          bookmarks[ix+1].strip())
        # remove header of empty folder <DT><H3 ADD_DATE="1500646543" LAST_MODIFIED="1500646582">test1</H3>
        bookmarks[ix-1] = ''
        # remove empty folder '<DL><p>','</DL><p>'
        bookmarks[ix+0], bookmarks[ix+1] = EMPTY_LINE, EMPTY_LINE
        
    return [x for x in bookmarks if x != '']

def delete_empty_folders_ff(bookmarks, verbose=False):
    '''TODO'''
    indices = [i for i,v in enumerate(pairwise([x.strip() for x in bookmarks
                                                if x.strip() > ''])) 
               if ''.join(v) == '<DL><p></DL><p>']

    for ix in indices:
        if verbose:
            print 'FF at index {} - folder {}, empty body {} {} '\
                  .format(ix,
                          bookmarks[ix+0].strip(),
                          bookmarks[ix+1].strip(),
                          bookmarks[ix+2].strip())
        # remove header of empty folder <DT><H3 ADD_DATE="1500646543" LAST_MODIFIED="1500646582">test1</H3>
        bookmarks[ix+0] = ''
        # remove empty folder '<DL><p>','</DL><p>'
        bookmarks[ix+1], bookmarks[ix+2] = '',''
        
    return [x for x in bookmarks if x != '']

def blank_empty_folder(bookmarks, indices):
    '''TODO'''
    # remove header of empty folder <DT><H3 ADD_DATE="1500646543" LAST_MODIFIED="1500646582">test1</H3>
    bookmarks[indices[0]] = ''
    # remove empty folder '<DL><p>','</DL><p>'
    bookmarks[indices[1]], bookmarks[indices[2]] = '',''
    
def delete_empty_folders_gen(bookmarks, verbose=False):
    '''TODO'''
    START_TAG, END_TAG = '<DL><p>','</DL><p>'
    FOLDER_PTRN = "<DT><H3.+?</H3>"
    FOLDER_HEAD_PTRN = "<DT><H3"
    FOLDER_TAIL_PTRN = "</H3>"
    OFFSET_TPL = (0,1,2)
    empty_folder_body_indices = [i for i,v in enumerate(pairwise([x.strip() for x in bookmarks
                                                if x.strip() > ''])) 
               if ''.join(v) == ''.join([START_TAG, END_TAG])]
    for ix in empty_folder_body_indices:
        #for shift, bm_type in zip((0,-1,), ('FF','CH',)):
        for shift, bm_type in zip((-1,), ('CH',)):
        #for shift, bm_type in zip((0,), ('FF',)):
            offset = [x+shift for x in OFFSET_TPL]
            if verbose: print offset, bm_type
            if ((bookmarks[ix+offset[1]].strip() == START_TAG)
                & (bookmarks[ix+offset[2]].strip() == END_TAG)):
                if verbose:
                    print offset[1], bookmarks[ix+offset[1]].strip()
                    print offset[2], bookmarks[ix+offset[2]].strip()
                if re.search(FOLDER_PTRN, bookmarks[ix+offset[0]]):
                    if verbose: print offset[0], bookmarks[ix+offset[0]].strip()
                else:
                    #handle split folder title
                    if re.search(FOLDER_TAIL_PTRN, bookmarks[ix+offset[0]]):
                        if verbose: print offset[0], bookmarks[ix+offset[0]]
                        bookmarks[ix+offset[0]] = ''
                        if re.search(FOLDER_HEAD_PTRN, bookmarks[ix+offset[0] - 1]):
                            if verbose: print offset[0] - 1, bookmarks[ix+offset[0] - 1]
                            bookmarks[ix+offset[0] - 1] = EMPTY_LINE
                        elif re.search(FOLDER_HEAD_PTRN, bookmarks[ix+offset[0] - 2]):
                            if verbose:
                                print offset[0] - 2, bookmarks[ix+offset[0] - 2]
                                print offset[0] - 1, bookmarks[ix+offset[0] - 1]
                            bookmarks[ix+offset[0] - 2] = EMPTY_LINE
                            bookmarks[ix+offset[0] - 1] = EMPTY_LINE
                        else: 
                            msg = 'Folder header split at index {}, containing {}'.format(
                                ix, bookmarks[ix+offset[0]].strip())
                            raise ValueError(msg)
                blank_empty_folder(bookmarks, [ix+x+shift for x in OFFSET_TPL])
            else:
                msg = 'Cannot re-bind to empty folder at index {}, offsets {}, shift {}'.format(
                    ix, OFFSET_TPL, shift)
                raise ValueError(msg)
        if verbose: print '-' * 20
    return [x for x in bookmarks if x != '']

def main(argv):
    ''''''
    # TODO - ask around whether argument parsing 
    # should be inside or outside the main() function
    SAVE_PARTIAL_DEDUP = False
    parser = argparse.ArgumentParser(
        description='Deduplicate bookmark HTML file.')
    parser.add_argument('infname',
                        metavar='INPUT',
                        type=str,
                        help='input file name')
    parser.add_argument('-b','--browser',
                        metavar='BROWSER',
                        choices=['ch', 'ff'],
                        help='source of exported bookmarks (default: ???)')
    parser.add_argument("-v", "--verbose",
                        action='store_true',
                        help="verbosity on")
    parser.add_argument("-l", "--links",
                        action='store_true',
                        help="produce file with URL list")
    args = parser.parse_args()
    if args.verbose:  print 'Arguments:', args
    INPUT = args.infname

    if args.browser == 'ch':
        global delete_empty_folders_chrome
        delete_empty_folders = delete_empty_folders_chrome
        if args.verbose: print 'SRC BROWSER set to [{}]'.format(args.browser)
    elif args.browser == 'ff':
        global delete_empty_folders_ff
        delete_empty_folders = delete_empty_folders_ff
        if args.verbose: print 'SRC BROWSER set to [{}]'.format(args.browser)
    else:
        delete_empty_folders = delete_empty_folders_gen
        if args.verbose: print 'SRC BROWSER {}'.format('autodetected')
    #
    # ingesting input HTML file
    bm = open(INPUT, 'r').readlines()
    # remove empty lines
    if args.verbose: print [x for x in bm if not x.strip(os.linesep).strip()]
    bm = [x for x in bm if x.strip(os.linesep).strip()]
    if args.verbose: print '# of lines in input: {}'.format(len(bm))
    # analysis of URLs
    url_counter = get_url_counter(bm)
    urls_list_input = list(url_counter)
    if args.verbose: print 'INPUT: {} unique URLs'.format(len(urls_list_input))
##    # to count only multiplicated URLs
##    print get_url_counter(bm, duped=True)
    #
    # letting pass only first instances of each URL
    bm = [entry for entry in bm if first_bookmark_filter(entry, url_counter, PTRN)]
    #
    # diagnostic list of unique URLs
    urls_list_deduped = list(get_url_counter(bm))
    if args.verbose: print 'DEDUPED: {} unique URLs'.format(len(urls_list_deduped))
    #
    # saving output with deduplicated URLs
    if SAVE_PARTIAL_DEDUP:
        outfname, ext = os.path.splitext(INPUT)
        outfname = '_'.join([outfname, 'partial']) + ext
        with open(outfname, 'w') as fout:
            fout.writelines(bm)
    #
    # deleting empty bookmark folders
    bm = delete_empty_folders_gen(bm, verbose=args.verbose)
    #
    # diagnostic list of unique URLs
    urls_list_cleaned = list(get_url_counter(bm))
    if args.verbose: print 'CLEANED: {} unique URLs'.format(len(urls_list_cleaned))
    #
    # saving completely cleaned output
    outfname, ext = os.path.splitext(INPUT)
    outfname = '_'.join([outfname, 'deduped']) + ext
    with open(outfname, 'w') as fout:
        fout.writelines(bm)
    #
    # saving deduped list of URLs
    if args.links:
        outfname, ext = os.path.splitext(INPUT)
        outfname = '_'.join([outfname, 'urls']) + '.txt'
        with open(outfname, 'w') as fout:
            fout.writelines([x + '\n' for x in sorted(urls_list_cleaned)])
    #
    # final diagnostics
    assert urls_list_input == urls_list_deduped, \
           'unique URLs differ between INPUT and DEDUPED'
    assert urls_list_deduped == urls_list_cleaned, \
           'unique URLs differ between DEDUPED and CLEANED'

if __name__ == "__main__":
    main(sys.argv)
