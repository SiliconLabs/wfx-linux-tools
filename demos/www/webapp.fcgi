#!/usr/bin/python3
from flup.server.fcgi import WSGIServer
from webapp_dispatcher import dispatch

# cgi: Common Gateway Interface support
# https://docs.python.org/3.7/library/cgi.html
import cgi

# cgitb: Traceback manager for CGI scripts
#  (only use cgitb during debug)
# https://docs.python.org/3.7/library/cgitb.html
# An alternative is :
#  import sys
#  sys.stderr = sys.stdout
#import cgitb

#cgitb.enable(display=1, logdir="/tmp/")

def myapp(environ, start_response):
    # We use collections.OrderedDict() instead of dict() because
    #  the web page refers to the json content as info[n].state,
    #  n being hardcoded as follows
    #  info[0]-> LED0
    #  info[1]-> LED1
    #  info[2]-> Connection (must be 'Connected' or 'Not Connected')
    #  info[3]-> STA_IP_address
    # As a consequence, the order of the following lines is FIXED
    try:
        start_response('200 OK', [('Content-Type', 'text/plain')])
      
        return dispatch(environ)
        
    except Exception as e:
        return str(e)


if __name__ == '__main__':
    WSGIServer(myapp, bindAddress='/tmp/fcgi.sock-0').run()
