#!/bin/python

###############################################
# Created by:  Aaron Ogle                     #
# Date: 05/05/2012                            #
#                                             #
#Project: libkiosk                            #
#                                             #
###############################################
import gtk
import webkit
import urllib
import string
import ctypes
import os
import time
import datetime
import threading
import gobject
import sys
import socket
#from OpenSSL import SSL
from subprocess import call

class XScreenSaverInfo( ctypes.Structure):
  """ typedef struct { ... } XScreenSaverInfo; """
  _fields_ = [('window',      ctypes.c_ulong), # screen saver window
              ('state',       ctypes.c_int),   # off,on,disabled
              ('kind',        ctypes.c_int),   # blanked,internal,external
              ('since',       ctypes.c_ulong), # milliseconds
              ('idle',        ctypes.c_ulong), # milliseconds
              ('event_mask',  ctypes.c_ulong)] # events

#-- Start of browser class --#

class browser():

	def __init__(self):
		self.serverip="10.10.10.27"
		self.serveraddress="http://" + self.serverip
		date = datetime.datetime.now()
		print "[Kiosk Started] - " + date.strftime("%B %d, %Y at %H:%M")
		self.whitelist = self.load_whitelist()
		
		self.view = webkit.WebView()
		
		self.ScrolledWindow = gtk.ScrolledWindow()
		self.ScrolledWindow.add(self.view)		

		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.fullscreen()
		
		self.home_image = gtk.Image()
		self.home_image.set_from_file("icons/Home.png")

		self.reload_image = gtk.Image()
		self.reload_image.set_from_file("icons/Reload.png")

		self.back_image = gtk.Image()
		self.back_image.set_from_file("icons/Back.png")

		self.home = gtk.Button(stock=gtk.STOCK_HOME)
		#self.home.add(self.home_image)

		self.reload = gtk.Button(stock=gtk.STOCK_REFRESH)
		#self.reload.add(self.reload_image)
	
		self.back = gtk.Button(stock=gtk.STOCK_GO_BACK)
		#self.back.add(self.back_image)

		self.progress = gtk.ProgressBar()

		self.nav = gtk.HBox()
		self.nav.pack_start(self.home, False)
		self.nav.pack_start(self.reload, False)
		self.nav.pack_start(self.back, False)

		self.vbox = gtk.VBox()
		self.vbox.pack_start(self.nav, False)
		self.vbox.pack_start(self.ScrolledWindow)
		
		self.status = gtk.HBox()
		self.status.pack_start(self.progress)
		self.vbox.pack_start(self.status, False)
		self.window.add(self.vbox)

		self.window.show_all()

		self.home.connect("clicked", self.homeclicked)
		self.view.connect("title-changed", self.title_changed)
		self.view.connect("load-progress-changed", self.load_progress_changed)
		self.view.connect("load-started", self.load_started)
		self.view.connect("load-finished", self.load_finished)
		self.reload.connect("clicked", self.reload_clicked)
		self.back.connect("clicked", self.back_clicked)
		self.view.connect("resource-request-starting", self.resource_cb)
		self.window.connect("destroy", self.destroy)
		
		self.view.open(self.serveraddress)
		self.homepage = True
		self.launchidlecheck()

	def main(self):
		gtk.main()

	def homeclicked(self,btn):
		self.sethome()

	def sethome(self):
		self.view.open(self.serveraddress)
		self.homepage = True

	def title_changed(self,webview, frame, title):
		self.window.set_title(title)

	def load_progress_changed(self,webview, amount):
		self.progress.set_fraction(amount / 100.0)

	def load_started(self,webview, frame):
		self.progress.show()

	def load_finished(self,webview, frame):
		self.progress.hide()

	def reload_clicked(self,btn):
		self.view.reload()

	def back_clicked(self,btn):
		self.view.go_back()

	def resource_cb(self,view, frame, resource, request, response):
		if self.isallowed(request.get_uri()) == -1:
			print request.get_uri() + " DENIED"
			request.set_uri(self.serveraddress)
			self.homepage = True

        def load_whitelist(self):
                whitelistfile = open("whitelisted", "r")
                lines = map(string.strip, whitelistfile.readlines())
                whitelistfile.close()
                return lines 

	def nullfunction(self):
		return

	def deny(self):
		return -1

	def isallowed(self,site):
		domain = ''
		try:	
			domain = site.split('/')[2]
		except IndexError:
			self.nullfunction()
		else:
			if site.split('/')[2] == -1:
				domain = self.server
		finally:
			if domain not in self.whitelist:
				return self.deny()
			else:
				if domain == self.serverip:
					self.homepage = True
				else:
					self.homepage = False
				return 1

	def destroy(self,widget, data=None):
		gtk.main_quit()

	def launchidlecheck(self):
		print "Starting Idle check function.."
		self.idlethread = threading.Thread(target=self.checkidle)
		self.idlethread.setDaemon(True)
		self.idlethread.start()

	def getidle(self):
		xlib = ctypes.cdll.LoadLibrary('libX11.so')
		display = xlib.XOpenDisplay(os.environ['DISPLAY'])
		xss = ctypes.cdll.LoadLibrary('libXss.so.1')
		xss.XScreenSaverAllocInfo.restype = ctypes.POINTER(XScreenSaverInfo)
		xssinfo = xss.XScreenSaverAllocInfo()
		xss.XScreenSaverQueryInfo(display, xlib.XDefaultRootWindow(display), xssinfo)
		return xssinfo.contents.idle


	def checkidle(self):
		print "In checkidle"
		while True:
			if self.homepage == False:
				print "Starting Idle Count"
				time.sleep(61)
				current = self.getidle()/1000
				print current
				print current/60
				
				#if 120s or 2 Min
				if(current > 120):
					self.sethome()
					print "Station reset"

		

#-- End of browser class --#

#-- Main --#

if __name__ == "__main__":
	try:
		app = browser()
		gtk.gdk.threads_enter()
		app.main()
	except Exception, e:
		date = datetime.datetime.now()
		print "[Error Occured] - " + date.strftime("%B %d, %Y at %H:%M")
		print "Error: %s" % (e)
		gtk.gdk.threads_leave()

#-- EOF --#
