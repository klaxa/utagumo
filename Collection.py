#!/usr/bin/python
import logging
import sqlite3

##################
# Database layout:
# Table Tracks:
# PRIMARY KEY ID | filename | title | artist | album 
#
# Table Encodes:
# ID | codec | quality | filename | hash
# Index: ID, codec, quality
#
##################

DATABASE="utagumo.db"

logging.basicConfig(level=logging.INFO)

class Track:
	def __init__(self, filename, title="Unknown Title", artist="Unknown Artist", album="Unknown Album", encodes = None, track_id=0):
		self.track_id = track_id
		self.filename = filename
		self.title = title
		self.artist = artist
		self.album = album
		self.encodes = encodes
		if encodes == None:
			self.encodes = dict()
		self.dirty = False
		# maybe persists in the constructor?
		
	def __repr__(self):
		return "<File: %s, Title: %s, Artist: %s, Album: %s>" % (self.filename, self.title, self.artist, self.album)
	
	def to_dict(self):
		result = dict()
		result["filename"] = self.filename
		result["title"] = self.title
		result["artist"] = self.artist
		result["album"] = self.album
		result["track_id"] = self.track_id
		return result

class Collection:
	def __init__(self, playlist_file):
		self.conn = sqlite3.connect(DATABASE, check_same_thread=False)
		c = self.conn.cursor()
		c.execute('CREATE TABLE IF NOT EXISTS Tracks (Id INTEGER PRIMARY KEY, Filename TEXT UNIQUE, Title TEXT, Artist TEXT, Album TEXT)')
		c.execute('CREATE TABLE IF NOT EXISTS Encodes (Id INTEGER, Codec TEXT, Quality TEXT, Filename TEXT, Hash TEXT)')
		c.execute('CREATE UNIQUE INDEX IF NOT EXISTS Key ON Encodes (Id, Codec, Quality)')
		self.conn.commit()
		#self.tracks = []
		if playlist_file is not None:
			self.tracks = self.parse_playlist_file(playlist_file)
		c.close()
	def db_write_track(self, track):
		c = self.conn.cursor()
		# use query plan, vms, etc.
		track_id = track.tack_id
		if get_track_by_filename(track.filename) == None:
			c.execute('INSERT INTO Tracks (Filename, Title, Artist, Album) VALUES(?, ?, ?, ?)', (track.filename, track.title, track.artist, track.album))
			track_id = c.lastrowid
		
		for codec in track.encodes:
			for quality in track.encodes[codec]:
				logging.info("Inserting: %s %s %s" % (track_id, codec, quality))
				c.execute('INSERT OR IGNORE INTO Encodes (Id, Codec, Quality, Filename, Hash) VALUES(?, ?, ?, ?, ?)', (track_id, codec, quality, track.encodes[codec][quality]["file"], track.encodes[codec][quality]["hash"]))
		self.conn.commit()
		track.dirty = False
		c.close()
		
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
		while True:
			key_and_length = line.split(",")[0]
			(key, length) = key_and_length.split(":")
			if key != "#EXTINF":
				logging.error("Error while parsing line: %s" % (line))
				return []
			title = ",".join(line.split(",")[1:])
			filename = pfile.readline().strip()
			track = Track(filename, title) # TODO: Get more metadata
			self.db_write_track(track)
			logging.info("Created Track %s" % (str(track)))
			line = pfile.readline()
			while not line.startswith("#EXTINF"):
				line = pfile.readline().strip()
				if line == "":
					pfile.close()
					return
	
	def _track_from_row(self, row):
		# insert encodes
		c = self.conn.cursor()
		c.execute('SELECT * FROM Encodes WHERE Id = ?', (row[0],))
		encode = c.fetchone()
		encodes = dict()
		while encode != None:
			codec = encode[1]
			quality = encode[2]
			if codec not in encodes.keys():
				encodes[codec] = dict()
			if quality not in encodes[codec].keys():
				encodes[codec][quality] = dict()
			encodes[codec][quality]["file"] = encode[3]
			encodes[codec][quality]["hash"] = encode[4]
			encode = c.fetchone()
		c.close()
		return Track(row[1], row[2], row[3], row[4], encodes, row[0])
	
	def _track_light_from_row(self, row):
		return Track(row[1], row[2], row[3], row[4], None, row[0])
	def get_track_by_id(self, track_id):
		c = self.conn.cursor()
		c.execute('SELECT * FROM Tracks WHERE Id = ?', (track_id,))
		row = c.fetchone()
		if row == None:
			return None
		c.close()
		return self._track_from_row(row)
	def get_track_by_filename(self, filename):
		c = self.conn.cursor()
		c.execute('SELECT * FROM Tracks WHERE Filename = ?', (filename,))
		row = c.fetchone()
		if row == None:
			return None
		c.close()
		return self._track_from_row(row)
	
	def get_all_tracks(self):
		c = self.conn.cursor()
		tracks = []
		c.execute('SELECT * FROM Tracks')
		row = c.fetchone()
		while row != None:
			tracks.append(self._track_from_row(row))
			row = c.fetchone()
		c.close()
		return tracks

if __name__ == "__main__":
	playlist = Collection("/home/klaxa/Music/test.m3u")
	print(str(playlist.get_tracks()))
