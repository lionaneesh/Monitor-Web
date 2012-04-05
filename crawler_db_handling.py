import sqlite3 as lite
from os import getcwd
from crawler_log import *
DB_NAME = 'web_monitor.db'

def db_connect():
    con = lite.connect(getcwd() + '/' + DB_NAME)
    c   = con.cursor()
    return c, con

def db_setup_everything(c, con):
    try:
        c.execute('SELECT * from cache')
    except lite.OperationalError:
        log("Creating cache")        
        c.execute("CREATE TABLE cache(url text, content text)")
    con.commit()

def db_get_data(pages, c):
    c.execute('SELECT * from cache')
    log("Loading cache")        
    
    #build up the lists
    while 1:
        try:    
            data = list(c.fetchone())
        except TypeError:
            break
        pages[data[0]] = data[1]
