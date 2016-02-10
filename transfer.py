__author__ = 'Kibur'

import os
import sys
import hashlib
from datetime import date, timedelta
import time
import threading

class BackgroundWorker(threading.Thread):
	lock = threading.Lock()

	def getObject(self):
		return self._obj

	def getWait(self):
		return self._wait

	def run(self):
        print '"%s" thread started' % (self.getName())

		while (not self.stopped()):
			try:
				time.sleep(self._wait)

				self.doWork()
			except:
				e = sys.exc_info()[0]
				print 'Debug: ', e
				self.stop()

		BackgroundWorker.lock.acquire()
		BackgroundWorker.lock.release()

		print '%s: %s \r' % (self.getName(), self._obj.getDigest())

	def doWork(self):
		self._obj.hashfile()

		if self._obj.getDigest() != None:
			self.stop()

	def stop(self):
		self._stop.set()

	def stopped(self):
		return self._stop.isSet()

	def __init__(self, w, obj):
		self._wait = w
		self._obj = obj

		super(BackgroundWorker, self).__init__()
		self._stop = threading.Event()

		BackgroundWorker.lock.acquire()
		BackgroundWorker.lock.release()

class Hasher:
	def getFilename(self):
		return self._filename

	def getBlockSize(self):
		return self._bs

	def getDigest(self):
		return self._hexdigest

	def setFilename(self, filename):
		self._filename = filename

	def setBlockSize(self, bs):
		self._bs = bs

	def hashfile(self):
		with open(self.getFilename(), 'rb') as afile:
			buf = afile.read(self.getBlockSize())
			hasher = hashlib.sha1()

			while len(buf) > 0:
				hasher.update(buf)
				buf = afile.read(self.getBlockSize())

			self._hexdigest = hasher.hexdigest()

	def __init__(self, filename=None):
		self._filename = filename
		self._bs = 65536
		self._hexdigest = None

class UI:
	def __init__(self):
		bwOrigHash.setName("local")
		bwOrigHash.daemon = False
		bwOrigHash.start()

		bwDestHash.setName("remote")
		bwDestHash.daemon = False
		bwDestHash.start()

		bwOrigHash.join()
		bwDestHash.join()

		if (bwOrigHash.isAlive() == False and bwDestHash.isAlive() == False):
			origHash = bwOrigHash.getObject()
			destHash = bwDestHash.getObject()

			if destHash.getDigest() == origHash.getDigest():
				try:
					os.remove(origHash.getFilename())
					print 'File "%s" removed' % (origHash.getFilename())
				except OSError, ose: # No such file or directory
					pass

if __name__ == '__main__':
	yesterday = date.today() - timedelta(1)
	filename = 'backup-' + yesterday.strftime('%d-%m-%Y')  + '.tar.gz'

	bwOrigHash = BackgroundWorker(5,\
		Hasher('/mnt/shares/' + filename))
	bwDestHash = BackgroundWorker(5,\
		Hasher('/mnt/shares/remote/bakups/' + filename))

	ui = UI()
