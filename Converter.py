#!/usr/bin/python

import subprocess
import os
import logging
import zlib
from Collection import Track

logging.basicConfig(level=logging.INFO)

FFMPEG="ffmpeg"

class Converter:
	def __init__(self):
		pass
	def encode(self, track, codec="opus", quality="64k"):
		# what if the same unencoded file gets requested rapidly?
		# is it overwritten while being encoded?
		filename = track.filename
		container = codec
		mode = "q"
		if "k" in quality:
			mode = "b"
		if codec == "vorbis":
			codec = "libvorbis"
			container = "ogg"
		if codec == "mp3":
			codec = "libmp3lame"
		logging.info("Checking for existing encode: track: %s track.encodes: %s quality: %s" % (track, str(track.encodes), quality))
		if codec in track.encodes and quality in track.encodes[codec]:
			encoded_file = track.encodes[codec][quality]["file"]
			logging.info("File is: %s" % (encoded_file))
			logging.info("Hash db: %s, Hash file: %s" % (track.encodes[codec][quality]["hash"], self.hash(encoded_file)))
			status = self.hash(encoded_file) == track.encodes[codec][quality]["hash"]
			logging.info("Hash db == Hash file: %s" % (status))
			if os.path.isfile(encoded_file) and self.hash(encoded_file) == track.encodes[codec][quality]["hash"]:
				logging.info("Encoded file (%s) already exists." % (track.encodes[codec][quality]["file"]))
				return track.encodes[codec][quality]["file"]
		encoded_file = "%s_%s_%s.%s" % (filename, codec, quality ,container)
		ffmpeg_command = [FFMPEG, "-i", filename, "-c:a", codec, "-%s:a" % (mode), quality, "-y", encoded_file]
		logging.info("ffmpeg command: %s" % (ffmpeg_command))
		ret = subprocess.call(ffmpeg_command)
		if ret != 0:
			logging.error("Error while encoding")
			return None
		track.dirty = True
		track.encodes[codec] = dict()
		track.encodes[codec][quality] = dict()
		track.encodes[codec][quality]["file"] = encoded_file
		track.encodes[codec][quality]["hash"] = self.hash(encoded_file)
		return encoded_file
	def hash(self, filename):
		file_to_hash = open(filename, "rb")
		hash_to_file = zlib.crc32(file_to_hash.read()) & 0xffffffff # apparently this is needed for compatibility
		file_to_hash.close()
		return str(hash_to_file)
