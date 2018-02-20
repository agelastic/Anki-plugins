# coding: utf-8

"""
Simple addon to quickly lookup words in the OSX dictionary

Author: Eddie Blundell <eblundell@gmail.com>
Heavily based of work by Artiom Basenko <demi.log@gmail.com>
https://gist.github.com/Xifax/f36002ddf910993d6bfb

License: The MIT License (MIT)
"""

# Stdlib

# Anki
from aqt.qt import *
from aqt.webview import AnkiWebView
from anki.hooks import addHook

# Qt
from PyQt4.QtGui import *
from PyQt4.QtCore import *


class OSXDictionary:
	"""OSX Dictionary launcher
	"""
	OSX_CMD = 'open dict:///%s'

	def get_selected(self, view):
		"""Copy selected text"""
		return view.page().selectedText()

	def lookup_osx(self, view):
		QProcess.startDetached(self.OSX_CMD % self.get_selected(view))

	def add_action(self, view, menu, action):
		"""Add 'lookup' action to context menu"""
		action = menu.addAction(action)
		action.connect(action, SIGNAL('triggered()'),
			lambda view=view: self.lookup_osx(view))

	def lookup_osx_action(self, view, menu):
		"""Lookup OSX action"""
		self.add_action(view, menu,
			u'Lookup "%s"' % self.get_selected(view)[:10])

# Add lookup actions to context menu
osx_dict = OSXDictionary()
addHook("AnkiWebView.contextMenuEvent", osx_dict.lookup_osx_action)
