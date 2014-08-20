#!/usr/bin/python

import logging
from Playlist import *
from Converter import *

logging.basicConfig(level=logging.INFO)

def main():
	playlist = Playlist("/home/klaxa/Music/test.m3u")
	converter = Converter()
	converter.encode(playlist.tracks[0])
	converter.encode(playlist.tracks[0])
main()
