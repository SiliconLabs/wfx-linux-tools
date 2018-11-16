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
firmware = bash_res("wfx_firmware_show | sed -ne 's/.*loaded version: *//p'")
driver   = bash_res("wfx_driver_show   | sed -ne 's/.*loaded version: *//p'")
checks   = bash_res('wfx_checks')

print ("Content-type:text/html\r\n\r\n")

print ("""
<!DOCTYPE html>
	<html lang="en">
	  <head>
		<meta charset="utf-8">
		<title>Silicon Labs WFX</title>
		<link rel="stylesheet" href="../html/silabs.css" type="text/css">
	  </head>
""")

print ("""
  <body>
	<div class="column">
		<div class="row">
			<br>
			<div class="column">
				<div class="row">
					<hr>
					<table>
						<tr>
							<td>
								<div class="logo">
									<a href="//www.silabs.com/" class="logo-link" id="sitelogo">
										<img src="../html/logo.png" alt="Silicon Labs" width="200"/>
									</a>
								</div>
							</td>
						</tr>
					</table>
					<hr>
				</div>
			</div>
		</div>
		<div class="row">
			<table>
				<tr>
					<td>
						<div class="logo">
							<img src="../html/BRD8022.png" alt="BRD" width="500"/>
						</div>
					</td>
				</tr>
			</table>
			<hr>
		</div>
		<div class="row">
			<h2 style="text-align:center;">Welcome to WFX!</h2>
			<hr>
		</div>
	</div>
  </body>
""")

print ("""<div class="column">""")

print ("<h4>%s</h4>"        % (date))
print ("<h2>%s</h2>"        % (model))
print ("<h2>Linux %s</h2>"  % (kernel))
print ("<h2>%s</h2>"        % (board))
print ("<h2>bus: %s</h2>"   % (bus))
print ("<h2>LAN  IP: %s</h2>"   % (bash_res("wfx_info ip eth")))
print ("<h2>WLAN IP: %s</h2>"   % (bash_res("wfx_info ip wlan")))

if "ap" in mode:
	print ("""<table border="1">""")
	print ("<tr>")
	print ("<td><h1>  %s mode</h1></td>"  % (mode))
	print ("<td>")
	print ("<ul>")
	print ("<h3>")
	print ("<li>%s</li>"  % (bash_res("wfx_info ap ssid")))
	print ("<li>%s</li>"  % (bash_res("wfx_info ap beacon_int")))
	print ("<li>%s</li>"  % (bash_res("wfx_info ap dtim")))
	print ("</h3>")
	print ("</ul>")
	print ("</td>")
	print ("</tr>")
	print ("</table>")

if "station" in mode:
	print ("<h2>%s mode</h2>"   % (mode))

print ("<h2>Driver %s</h2>" % (driver))
print ("<h2>%s</h2>"        % (firmware))
print ("<hr>")

print ("""<table border="1">""")
print ("<tr>")
print ("<td><h1>%s</h1></td>"  % "WFX Checks")
print ("<td>")
print ("<ul>")
print ("<h3>")
for line in checks.splitlines():
	print ("<li>%s\n</li>"       % (line))
print ("</h3>")
print ("</ul>")
print ("</td>")
print ("</tr>")
print ("</table>")

print ("""</div>""")

print ("""
	  </body>
	</html>
""")
