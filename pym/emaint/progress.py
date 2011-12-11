#!/usr/bin/python -O
# vim: noet :
#
# Copyright 2010 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2 or later
#
# $Header$


from __future__ import print_function


import time
import signal

import portage


class ProgressHandler(object):
	def __init__(self):
		self.reset()

	def reset(self):
		self.curval = 0
		self.maxval = 0
		self.last_update = 0
		self.min_display_latency = 0.2

	def onProgress(self, maxval, curval):
		self.maxval = maxval
		self.curval = curval
		cur_time = time.time()
		if cur_time - self.last_update >= self.min_display_latency:
			self.last_update = cur_time
			self.display()

	def display(self):
		raise NotImplementedError(self)


class ProgressBar(ProgressHandler):
	"""Class to set up and return a Progress Bar"""

	def __init__(self, isatty):
		self.isatty = isatty
		ProgressHandler.__init__(self)

	def start(self):
		if self.isatty:
			self.progressBar = portage.output.TermProgressBar()
			signal.signal(signal.SIGWINCH, self.sigwinch_handler)
		else:
			self.onProgress = None
		return self.onProgress

	def display(self):
		self.progressBar.set(self.curval, self.maxval)

	def sigwinch_handler(signum, frame):
		lines, self.progressBar.term_columns = \
			portage.output.get_term_size()

	def stop(self):
		signal.signal(signal.SIGWINCH, signal.SIG_DFL)
