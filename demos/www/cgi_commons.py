#!/usr/bin/python3
# We need to call bash scripts to execute command with superuser
#   privileges when called from a web page
# This works as long as all scripts are chmod'ed with a+rx

import subprocess
import sys
import time
import collections

# cgi: Common Gateway Interface support
# https://docs.python.org/3.7/library/cgi.html
import cgi
# cgitb: Traceback manager for CGI scripts
#  (only use cgitb during debug)
# https://docs.python.org/3.7/library/cgitb.html
# An alternative is :
#  import sys
#  sys.stderr = sys.stdout
import cgitb

cgitb.enable(display=1, logdir="/tmp/")
profiling=list()
start_time = time.clock()
prev_time = start_time

def bash_res(cmd, trace=0):
    trace_cmd = 0
    trace_res = 0
    if str(trace).isdigit():
        trace = int(str(trace))
        if trace > 1:
            trace_cmd = (trace >> 1) & 0x1
            trace_res = (trace >> 2) & 0x1
        else:
            trace_cmd = trace
            trace_res = trace
    else:
        trace = 0
    if trace_cmd:
        print("<>cmd<>" + cmd + "<>cmd<>")
    res = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    ret = res.stdout.read().strip()
    if trace_res:
        print("<>res<>" + ret + "<>res<>")
    return ret.decode()

def dmesg_print(txt):
    bash_res("echo " + called_script + ": " + txt + " | sudo tee  /dev/kmsg")

def profile(txt="", from_start=None):
    global start_time
    global prev_time
    p = collections.OrderedDict()
    if from_start is None:
        p[txt] = str.format("%d" % ((time.clock() - prev_time)*1000))
    else:
        p[txt] = str.format("%d" % ((time.clock() - start_time)*1000))
    prev_time = time.clock()
    profiling.append(p)

form = cgi.FieldStorage()
# example: if "item" not in form:
#    print("Please fill in the " + "item" + " name field (use 'item=<value>).")
#    return
# example: item = form.getvalue("item")
# example (more robust to 'hackers'): led_id=form.getfirst("led_id","")

called_script = sys.argv[0]

if "trace" in form:
    trace = form["trace"].value
else:
    trace = '0'
