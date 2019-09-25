#!/usr/bin/python
# We need to call bash scripts to execute command with superuser
#   privileges when called from a web page
# This works as long as all scripts are chmod'ed with a+rx
from cgi_commons import *

if "led_id" not in form:
    print("Argument error: A proper request is 'led_toggle.cgi?led_id=0/1'")
else:
    # Use form.getfirst as a measure of protection against hackers
    led_id=form.getfirst("led_id","")
    # Check that led_id is a digit as a measure of protection against hackers
    if led_id.isdigit():
        bash_res("./led_toggle.sh " + led_id, trace)
    else:
        print("Argument error: led_id is not an int")
    print(led_id)
