#!/usr/bin/python

# maybe write this as a cgi script?

from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
import threading
import logging
import json
from Collection import Collection, Track
from Converter import Converter

logging.basicConfig(level=logging.INFO)

class Handler(BaseHTTPRequestHandler):

	def send_file(self, filename):
		file_to_send = open(filename, "rb")
		self.wfile.write(file_to_send.read())

	def send(self, data):
		self.wfile.write(bytes(data, 'utf-8'))
	
	def send_track(self, args):
		track_id = args[0]
		quality = "64k"
		codec = "opus"
		if len(args) > 2:
			logging.info("Requested track multiple options")
			codec = args[2]
			if len(args) > 4:
				quality = args[4]
		converter = Converter()
		track = collection.tracks[int(args[0])]
		encoded_file = converter.encode(track, codec=codec, quality=quality)
		self.send_response(200)
		self.end_headers()
		self.send_file(encoded_file)
	
	def send404(self):
		self.send_response(404)
		self.end_headers()
		self.send("Not what you were looking for...")
		self.send('\n')
		return
	
	def send_collection(self):
		self.send_response(200)
		self.end_headers()
		files = list(map(Track.to_dict, collection.tracks))
		print(files)
		self.send(json.dumps(files))
		self.send('\n')
	
	
	def do_GET(self):
		logging.info("Working on GET request")
		logging.info("Client (%s,%s)" % self.client_address)
		logging.info("Path %s" % (self.path))
		
		# Do we have GET requests? I don't think so...
		self.send404()
		
		return
	
	def do_POST(self):
		logging.info("Working on GET request")
		logging.info("Client (%s,%s)" % self.client_address)
		logging.info("Path %s" % (self.path))
		path_args = self.path.split("/")
		logging.info("Path args: %s" % (str(path_args)))
		
		if path_args[1] == "api":
			if path_args[3] == "collection":
				self.send_collection()
			elif path_args[3] == "track" and len(path_args) > 4:
				self.send_track(path_args[4:])
			else:
				self.send_404()
		else:
			self.send_404()
		return
		
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	"""Handle requests in a separate thread."""

if __name__ == '__main__':
	server = ThreadedHTTPServer(('localhost', 8080), Handler)
	collection = Collection("/home/klaxa/Music/test.m3u")
	print('Starting server, use <Ctrl-C> to stop')
	server.serve_forever()
