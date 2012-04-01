import sys
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''

#-- Print diff --
def print_diff(msg):
    out = ''
    for m in msg.split('\n'):
        if m.startswith(('http://', 'https://',)):
            out += bcolors.OKBLUE + m + bcolors.ENDC + '\n'
        elif m.startswith('+'):
            out += bcolors.OKGREEN + m + bcolors.ENDC + '\n'
        elif m.startswith('-'):
            out += bcolors.FAIL + m + bcolors.ENDC + '\n'
        else:
            out += m + '\n'
    sys.stderr.write(out)
#-- Error --
def log(msg):
    print bcolors.OKGREEN + 'log: ' + msg + bcolors.ENDC

def warning(msg):
    print bcolors.WARNING + 'Warning: ' + msg + bcolors.ENDC

def error(msg):
    print bcolors.WARNING + 'Error: '   + msg + bcolors.ENDC

def fatal(msg):
    print bcolors.FAIL    + 'Fatal: '   + msg + bcolors.ENDC
    exit()

# @param msg      Error/Warning Message
# @param severity How severe the error is
# @return void
def error(msg, severity=1):
    if severity > 3 or severity < 0:
        severity = 3
    options = {
                0 : log,
                1 : warning,
                2 : error,
                3 : fatal
              }
    options[severity](msg)

#-- Prompt --

def casual_prompt(msg, possible_ans=''):
    return raw_input(bcolors.WARNING + msg + possible_ans + bcolors.ENDC + ' : ')

def important_prompt(msg, possible_ans=''):
    return raw_input(bcolors.FAIL + msg + possible_ans + bcolors.ENDC + ' : ')

# @param  msg      Prompt Message
# @param  severity How important the question is
# @return user_input
def prompt(msg, severity=1, possible_ans=''):
    if severity > 2 or severity < 1:
        severity = 2
    options = {
                1 : casual_prompt,
                2 : important_prompt
              }
    return options[severity](msg, possible_ans)

