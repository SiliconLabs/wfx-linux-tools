#!/usr/bin/python

# Import modules for CGI handling
import cgi, cgitb
import subprocess


def bash_res (cmd):
    res = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    return res.stdout.read()

date     = bash_res("date")
kernel   = bash_res("uname -r")
board    = bash_res("wfx_board")
model    = bash_res("cat /sys/firmware/devicetree/base/model")
bus      = bash_res("wfx_bus_show")
mode     = bash_res("pidof hostapd > /dev/null && echo ap || pidof wpa_supplicant > /dev/null && echo sta || echo none")
firmware = bash_res("wfx_firmware_show | sed -ne 's/.*loaded version: *//p'")
driver   = bash_res("wfx_driver_show   | sed -ne 's/.*loaded version: *//p'")
checks   = bash_res('wfx_checks')
hostname = bash_res('hostname')

print ("Content-type:text/html\r\n\r\n")

print ("""
<!DOCTYPE html>
	<html lang="en">
	  <head>
		<meta charset="utf-8">
		<title>Silicon Labs WFX</title>
		<link rel="stylesheet" href="/silabs.css" type="text/css">
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
										<img src="/logo.png" alt="Silicon Labs" width="200"/>
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
							<img src="/BRD8022.png" alt="BRD" width="500"/>
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

if 1:
	print ("""<table border="1">""")
	print ("<tr>")
	print ("<td><h1>%s</h1></td>"  % "System information")
	print ("<td>")
	print ("<ul>")
	print ("<h3>")
	print ("<li>%s</li>"  % (model))
	print ("<li>Kernel %s</li>"  % (kernel))
	print ("<li>Hostname: %s</li>"  % (hostname))
	print ("<li>EXP board:%s</li>"  % (board))
	print ("<li>Bus: %s</li>"  % (bus))
	print ("<li>Driver:   %s</li>"  % (driver))
	print ("<li>Firmware: %s</li>"  % (firmware))

	print ("</h3>")
	print ("</ul>")
	print ("</td>")
	print ("</tr>")
	print ("</table>")

if 1:
	print ("""<table border="1">""")
	print ("<tr>")
	print ("<td><h1>%s</h1></td>"  % "IP addresses")
	print ("<td>")
	print ("<ul>")
	print ("<h3>")
	print ("<li>LAN  %s</li>"  % (bash_res("wfx_info ip eth")))
	print ("<li>WLAN %s</li>"  % (bash_res("wfx_info ip wlan")))
	print ("</h3>")
	print ("</ul>")
	print ("</td>")
	print ("</tr>")
	print ("</table>")

if 1:
	print ("""<table border="1">""")
	print ("<tr>")
	print ("<td><h1>%s</h1></td>"  % "MAC addresses")
	print ("<td>")
	print ("<ul>")
	print ("<h3>")
	print ("<li>LAN  %s</li>"  % (bash_res("wfx_info mac eth")))
	print ("<li>WLAN %s</li>"  % (bash_res("wfx_info mac wlan")))
	print ("</h3>")
	print ("</ul>")
	print ("</td>")
	print ("</tr>")
	print ("</table>")

if "ap" in mode:
	print ("""<table border="1">""")
	print ("<tr>")
	print ("<td><h1>  %s mode</h1></td>"  % (mode))
	print ("<td>")
	print ("<ul>")
	print ("<h3>")
	print ("<li>%s</li>"  % (bash_res("wfx_info ap ssid")))
	print ("<li>%s</li>"  % (bash_res("wfx_info ap mgmt")))
	print ("<li>%s</li>"  % (bash_res("wfx_info ap wpa=")))
	print ("<li>%s</li>"  % (bash_res("wfx_info ap channel")))
	print ("</h3>")
	print ("</ul>")
	print ("</td>")
	print ("</tr>")
	print ("</table>")

if "station" in mode:
	print ("""<table border="1">""")
	print ("<tr>")
	print ("<td><h1>  %s mode</h1></td>"  % (mode))
	print ("<td>")
	print ("<ul>")
	print ("<h3>")
	print ("<li>%s</li>"  % (bash_res("wfx_info station country")))
	print ("<li>%s</li>"  % (bash_res("wfx_info station wpa_state")))
	print ("<li>%s</li>"  % (bash_res("wfx_info station ^address")))
	print ("</h3>")
	print ("</ul>")
	print ("<ul>")
	print ("<h2>Visible Access Points</h2>")
	print ("<h3>")
	scan_res = bash_res("wfx_info station scan")
	for line in scan_res.splitlines():
		print ("<li>%s\n</li>"       % (line))
	print ("</h3>")
	print ("</ul>")
	print ("</td>")
	print ("</tr>")
	print ("</table>")

if 1:
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
