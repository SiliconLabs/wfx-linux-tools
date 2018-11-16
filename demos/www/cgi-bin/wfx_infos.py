#!/usr/bin/python

# Import modules for CGI handling 
import cgi, cgitb 
import subprocess


def bash_res (cmd):
	res = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
	return res.stdout.read()
	
date     = bash_res("date")
kernel   = bash_res("wfx_kernel")
board    = bash_res("wfx_board")
model    = bash_res("wfx_model")
bus      = bash_res("wfx_bus")
mode     = bash_res("wfx_mode")
firmware = bash_res("wfx_firmware | grep Label ")
driver   = bash_res("modinfo wfx | grep ^version")
checks   = "wfx_checks"

print ("<h4>%s</h4>"        % (date))
print ("<h2>%s</h2>"        % (model))
print ("<h2>Linux %s</h2>"  % (kernel))
print ("<h2>%s</h2>"        % (board))
print ("<h2>bus: %s</h2>"   % (bus))
print ("<h2>%s mode</h2>"   % (mode))
print ("<h2>Driver %s</h2>" % (driver))
print ("<h2>%s</h2>"        % (firmware))
print ("<h3>%s</h3>"        % (checks))
