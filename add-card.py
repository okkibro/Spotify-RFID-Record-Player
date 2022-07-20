#!/usr/bin/env python

from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from time import sleep
from dotenv import load_dotenv
import os
from urllib.parse import urlparse

load_dotenv()

DEVICE_ID = os.getenv("DEVICE_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

try:
        print("Before reading card: play song on Spotify account that is going to be authenticated that the new card should be paired with.")
        reader = SimpleMFRC522()
        card_id = str(reader.read()[0])
        print("The ID for this card is:", card_id)
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,client_secret=CLIENT_SECRET,redirect_uri="http://localhost:8080",scope="user-read-playback-state,user-modify-playback-state"))
        track_info = sp.current_user_playing_track()
        track_href = urlparse(track_info["item"]["href"])
        track_id = track_href.path.rsplit("/", 1)[-1]
        print("The ID for this track is:", track_id)
        print("Creating association in file and exiting...")
        with open("card-track-dictionairy.csv", "a+") as f:
                f.write(card_id + "," + track_id + "\n")

finally:
        GPIO.cleanup()
