#!/bin/python
# Copyright (c) 2012-2013 Aneesh Dogra <lionaneesh@gmail.com>

from BeautifulSoup import BeautifulSoup
import HTMLParser
import optparse
import urllib2
import sys
import os
from urlparse import urljoin # to support relative urls
import re                    # url checking
import signal                # for handling KeyboardInterrupts
from crawler_config import * # for handling Cralwer configurations
from errors import *
import datetime
import difflib
from crawler_db_handling import *
from time import time

def checkUrl(url) :
    # django regex for url validation

    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    if re.search(regex, url) == None :
        return 0
    else :
        return 1

def handle_SIGINT(signal, frame) :
    save_all()
    print_summary()
    error("Ctrl + C, Detected!\nExiting Now!", 3)

def print_summary():
    for changes in web_diff:
        try:
            print_diff(changes + web_diff[changes])
        except UnicodeDecodeError:
            sys.stderr.write('UnicodeError: ' + bcolors.OKBLUE + changes + bcolors.ENDC)

def save_all():
    for i in pages:
            c.execute("SELECT * from cache where url=\'%s\'" % (i,))
            data = c.fetchone()
            if data != None:
                c.execute("UPDATE cache SET content=\'%s\' where url=\'%s\'" % (pages[i], i,))
            else:
                c.execute("INSERT INTO cache(url, content) values(\'%s\', \'%s\')" % (i, pages[i],))
    con.commit()

web_list = read_config()

# connect to sqlite database  
data     = []
crawled  = []
tracked_pages = []
to_crawl = []
index    = {}
graph    = {}
content  = ''
pages    = {}
web_diff = {}
prefixes = ('http://', 'https://') # prefixes to check whether the link is an absolute link
c, con = db_connect()
db_setup_everything(c, con)
# db_get_data(crawled, to_crawl, pages, c)
db_get_data(pages, c)
if len(sys.argv) == 2:
    error("No directory Provided, Using %s as default" % os.getcwd(), 1)
#---- main -----
signal.signal(signal.SIGINT, handle_SIGINT)

for entry in pages:
    tracked_pages.append(entry)

for website in web_list:
    to_crawl.append(website.strip())
    for current_url in to_crawl :
        diff = ''
        if checkUrl(current_url) == 0 :
            to_crawl.remove(current_url)
            continue
        error("Crawling [%s]" % current_url, 0)
        try :
            req = urllib2.Request(current_url)
            req.add_header('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11')
            html_page = urllib2.urlopen(req)
        except urllib2.URLError as reason :
            error("URLError : %s" % (reason,), 2)
            continue
        except  ValueError :
            error("Invalid URL : %s" % current_url, 2)
            continue
        except KeyboardInterrupt :
            cleanup();
        source      = html_page.read()
        soup        = BeautifulSoup(source)
        content     = soup.prettify()
        minus = 0
        add = 0
        if current_url in tracked_pages:
            # See if there is any difference in the page
            len_diff = 0            
            cmp1 = content.split('\n')
            cmp1.pop() # @HACK
            tp   = open(pages[current_url])
            cmp2 = tp.readlines()
            length = len(cmp1)
            if len(cmp2) < length:
                length = len(cmp2)
                len_diff = 2 # 2 means cmp2 < cmp1
            for i in range(0, length):
                if cmp1[i].strip('\n') != cmp2[i].strip('\n'):
                    for ref in cmp2[i-4:i]:
                        diff += " %s\n" % (ref,)
                    diff += "- %s\n+ %s\n" % (cmp1[i].strip('\n'), cmp2[i].strip('\n'),)
                    add = add + 1
                    minus = minus + 1
                    for ref2 in cmp2[i+1:i+4]:
                        diff += " %s\n" % (ref2,)            
            if len_diff > 0:
                if len_diff == 1:
                    if extra in cmp2[length:]:
                        diff += "- %s\n" % (extra.strip('\n'),)
                        minus = minus + 1
                else:
                    if extra in cmp1[length:]:
                        diff += "+ %s\n" % (extra.strip('\n'),)
                        add = add + 1
            if diff == '': # no difference == No point of creating another cache file
                continue
            web_diff[current_url] = '\n%d Additions, %d Deletions\n- previous\n+ present\n' % (add, minus,) + diff
            os.remove(pages[current_url])
        else: # new page added
            content_list = content.split('\n')
            for a in content_list:
                diff += "+ %s\n" % (a,)
                add = add + 1
            web_diff[current_url] = '\nNew Page Added\n%d Additions, %d Deletions\n' % (add, minus) + diff
        temp = os.getcwd() + "/cache/cache.%.7f.html" % time()
        fp   = open(temp, 'w')
        fp.write(content)
        fp.close()
        anchor_tags = soup('a', limit = 100) # find at max 100 anchor tags from a webpage
        for tag in anchor_tags :
            try:
                url = tag['href']
            except KeyError:
                continue
            if url.startswith('#') :             # Anchor Tags pointing to the same page
                continue
            if url.startswith(prefixes) == True: # We dont want to link to other sites
                continue
            else : # relative link, we'll get a ton of invalid links here , example href='javascript:' etc.
               url = urljoin(current_url, url);
               if checkUrl(current_url) == 0:
                    continue
            if url not in to_crawl and url not in crawled:
                to_crawl.append(url)
                try:
                    # @TODO: Add Graph table
                    graph[current_url].append(url)
                except KeyError:
                    graph[current_url] = [url]
        pages[current_url] = temp
        crawled.append(current_url)
        to_crawl.remove(current_url)
save_all()
print_summary()
