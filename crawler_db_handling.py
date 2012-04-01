import sqlite3 as lite
from os import getcwd
from errors import *
DB_NAME = 'web_monitor.db'

def db_connect():
    con = lite.connect(getcwd() + '/' + DB_NAME)
    c   = con.cursor()
    return c, con

def db_setup_everything(c, con):
    try:
        c.execute('SELECT * from cache')
    except lite.OperationalError:
        error("Creating cache", 2)        
        c.execute("CREATE TABLE cache(url text, content text)")
#    try:
#        c.execute('SELECT * from crawled')
#    except lite.OperationalError:
#        c.execute("CREATE TABLE crawled(url text)")
#    try:
#        c.execute('SELECT * from to_crawl')
#    except lite.OperationalError:
#        c.execute("CREATE TABLE to_crawl(url text)")
#        c.execute("INSERT INTO to_crawl values(\'%s\')" % ('http://google.com',))

    con.commit()

def db_get_data(pages, c):
    c.execute('SELECT * from cache')

    #build up the lists
    while 1:
        try:    
            data = list(c.fetchone())
        except TypeError:
            break
        pages[data[0]] = data[1]

    print pages

#    c.execute('SELECT * from crawled')
#    data = c.fetchone()
    
    #build up the lists
#    while data != None:    
#        crawled.append(data)
#        crawled_pages.append(data[1])
#    
#    c.execute('SELECT * from to_crawl')
#    data = c.fetchone()    
#
#    while data != None:    
#        to_crawl.append("%s" % data)
#        data = c.fetchone()
