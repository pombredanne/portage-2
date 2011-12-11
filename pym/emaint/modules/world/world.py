#!/usr/bin/python -O
# vim: noet :

from __future__ import print_function


import portage
from portage import os



class WorldHandler(object):

	short_desc = "Fix problems in the world file"

	def name():
		return "world"
	name = staticmethod(name)

	def __init__(self):
		self.invalid = []
		self.not_installed = []
		self.invalid_category = []
		self.okay = []
		from portage._sets import load_default_config
		setconfig = load_default_config(portage.settings,
			portage.db[portage.settings['EROOT']])
		self._sets = setconfig.getSets()

	def _check_world(self, onProgress):
		categories = set(portage.settings.categories)
		eroot = portage.settings['EROOT']
		self.world_file = os.path.join(eroot, portage.const.WORLD_FILE)
		self.found = os.access(self.world_file, os.R_OK)
		vardb = portage.db[eroot]["vartree"].dbapi

		from portage._sets import SETPREFIX
		sets = self._sets
		world_atoms = list(sets["selected"])
		maxval = len(world_atoms)
		if onProgress:
			onProgress(maxval, 0)
		for i, atom in enumerate(world_atoms):
			if not isinstance(atom, portage.dep.Atom):
				if atom.startswith(SETPREFIX):
					s = atom[len(SETPREFIX):]
					if s in sets:
						self.okay.append(atom)
					else:
						self.not_installed.append(atom)
				else:
					self.invalid.append(atom)
				if onProgress:
					onProgress(maxval, i+1)
				continue
			okay = True
			if not vardb.match(atom):
				self.not_installed.append(atom)
				okay = False
			if portage.catsplit(atom.cp)[0] not in categories:
				self.invalid_category.append(atom)
				okay = False
			if okay:
				self.okay.append(atom)
			if onProgress:
				onProgress(maxval, i+1)

	def check(self, onProgress=None):
		self._check_world(onProgress)
		errors = []
		if self.found:
			errors += ["'%s' is not a valid atom" % x for x in self.invalid]
			errors += ["'%s' is not installed" % x for x in self.not_installed]
			errors += ["'%s' has a category that is not listed in /etc/portage/categories" % x for x in self.invalid_category]
		else:
			errors.append(self.world_file + " could not be opened for reading")
		return errors

	def fix(self, onProgress=None):
		world_set = self._sets["selected"]
		world_set.lock()
		try:
			world_set.load() # maybe it's changed on disk
			before = set(world_set)
			self._check_world(onProgress)
			after = set(self.okay)
			errors = []
			if before != after:
				try:
					world_set.replace(self.okay)
				except portage.exception.PortageException:
					errors.append("%s could not be opened for writing" % \
						self.world_file)
			return errors
		finally:
			world_set.unlock()
