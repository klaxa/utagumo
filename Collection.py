#!/usr/bin/python
import logging

logging.basicConfig(level=logging.INFO)

class Track:
	def __init__(self, filename, title="Unknown Title", artist="Unknown Artist", album="Unknown Album"):
		self.filename = filename
		self.title = title
		self.artist = artist
		self.album = album
		self.encodes = dict()
	def __repr__(self):
		return "<File: %s, Title: %s, Artist: %s, Album: %s>" % (self.filename, self.title, self.artist, self.album)
	
	def to_dict(self):
		result = dict()
		result["filename"] = self.filename
		result["title"] = self.title
		result["artist"] = self.artist
		result["album"] = self.album
		return result

class Collection:
	def __init__(self, playlist_file):
		self.tracks = []
		
		if playlist_file is not None:
			self.tracks = self.parse_playlist_file(playlist_file)
	
	def parse_playlist_file(self, playlist_file):
		# #EXTINF:123, Sample artist - Sample title
		# C:\Documents and Settings\I\My Music\Sample.mp3
		logging.info("Started parsing %s" % (playlist_file))
	
		pfile = open(playlist_file, "r")
		line = pfile.readline().strip()
		if line != "#EXTM3U":
			logging.error("File \"%s\" does not appear to be an m3u playlist!\n" % (playlist_file))
			logging.error("Line was \"%s\"" % (line))
			return []
		line = pfile.readline().strip()
		tracks = []
		while True:
			key_and_length = line.split(",")[0]
			(key, length) = key_and_length.split(":")
			if key != "#EXTINF":
				logging.error("Error while parsing line: %s" % (line))
				return []
			title = ",".join(line.split(",")[1:])
			filename = pfile.readline().strip()
			track = Track(filename, title) # TODO: Get more metadata
			logging.info("Created Track %s" % (str(track)))
			tracks.append(track)
			line = pfile.readline()
			while not line.startswith("#EXTINF"):
				line = pfile.readline().strip()
				if line == "":
					pfile.close()
					return tracks
if __name__ == "__main__":
	playlist = Collection("/home/klaxa/Music/test.m3u")
	print(str(playlist.get_tracks()))
