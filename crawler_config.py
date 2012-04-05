import os
from crawler_log import *

default_config_list = ['http://google.com']

def create_config(config='website-list.txt') :
    yes = ('Y', 'y', 'Yes', 'yes')
    no = ('N', 'n', 'No', 'no')
    usr_inp = ''
    if os.path.isfile(config):
        while usr_inp not in yes and user_inp not in no:
            usr_inp = prompt('%d file found, Overwrite' % config, 2, ' [Y/N] ')
        if usr_inp in no :
            config = prompt('Please enter new config file path', 1)
    try:     
        fp = open(config, 'w')
    except IOError:  
        error('Failed to write config file', 3)
    for i in default_config_list:
        fp.write(i + '\n')
        
def read_config(config="website-list.txt", dr=os.getcwd()) :
    try:
        fp = open(dr + '/' + config, 'r')
        comment_prefixes = ('#', '//')
        url_prefixes     = ('http://', 'https://')
        lines            = fp.readlines()
        web_list         = []    
    
        for line in range(0, len(lines)):
            if lines[line].startswith(comment_prefixes) or len(lines[line]) < 5:
                pass
            elif not lines[line].startswith(url_prefixes):
                error('The configuration file, line: %d is not in correct format, Ignoring this line.' % line_no + 1, 1)
            else:        
                web_list.append(lines[line])
        
    except IOError:
        error('No config file found or config file not readable. Creating one for you', 2)
        create_config(cwd + '/' + config)
        return default_config_list
    return web_list
