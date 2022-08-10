#!/usr/bin/env python

from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from time import sleep
from dotenv import load_dotenv
import os
from urllib.parse import urlparse
import sys

load_dotenv()

DEVICE_ID = os.getenv("DEVICE_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

while True:
    try:
        # Determine type of entry to be added
        type = None
        while type is None:
            raw_type = input("What do you want to add? Type [A] for album, [T] for track, [R] for artist, or [P] for playlist (or [Q] to quit): ")
            if raw_type.lower() == "[a]" or raw_type.lower() == "a":
                type = "album"
            elif raw_type.lower() == "[t]" or raw_type.lower() == "t":
                type = "track"
            elif raw_type.lower() == "[r]" or raw_type.lower() == "r":
                type = "artist"
            elif raw_type.lower() == "[p]" or raw_type.lower() == "p":
                type = "playlist"
            elif raw_type.lower() == "[q]" or raw_type.lower() == "q":
                sys.exit()
            else:
                print("Couldn't recognize type! Try again...")

        # Read card and get current song information
        print(f"Adding {type}! Play {type} on raspotify device and then hold card to reader.")
        reader = SimpleMFRC522()
        card_id = str(reader.read()[0])
        print("The ID for this card is:", card_id)
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,client_secret=CLIENT_SECRET,redirect_uri="http://localhost:8080",scope="user-read-playback-state,user-modify-playback-state"))
        track_info = sp.current_user_playing_track()

        # Get correct information based on type
        if type == "album":
            uri = track_info["item"]["album"]["uri"]
            name = track_info["item"]["album"]["name"]
        elif type == "track":
            uri = track_info["item"]["uri"]
            name = track_info["item"]["name"]
        elif type == "artist":
            uri = track_info["item"]["artists"][0]["uri"]
            name = track_info["item"]["artists"][0]["name"]
        elif type == "playlist":
            uri = track_info["context"]["uri"]
            name = "[custom playlist]"

        # Add card and corresponding information to dictionairy
        print(f"The URI for this {type} is: {uri}")
        print("Creating association in file and exiting...")
        with open("card-dictionairy.csv", "a+") as f:
                f.write(card_id + "," + uri + "," + type + "," + name + "\n")

    finally:
        print("Cleaning up and starting over...")
        GPIO.cleanup()
