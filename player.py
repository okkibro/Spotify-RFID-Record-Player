#!/usr/bin/env python

from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from time import sleep
from dotenv import load_dotenv
import os
import csv

load_dotenv()

DEVICE_ID = os.getenv("DEVICE_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

card_song_dict = {}

with open('card-track-dictionairy.csv', mode='r') as f:
    reader = csv.reader(f)
    card_song_dict = {rows[0]:rows[1] for rows in reader}

while True:
    try:
        reader=SimpleMFRC522()
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,client_secret=CLIENT_SECRET,redirect_uri="http://localhost:8080",scope="user-read-playback-state,user-modify-playback-state"))

        # Create an infinite while loop that will always be waiting for a new scan
        while True:
            print("Waiting for record scan...")
            card_id = reader.read()[0]
            print("Read succesful! Finding track corresponding to card...")
            sleep(2)
            try:
                song_uri = card_song_dict[str(card_id)]
                spotify_uri = "spotify:track:" + song_uri
                print("Track matched to card! Playing...")
                sp.transfer_playback(device_id=DEVICE_ID, force_play=False)
                sp.start_playback(device_id=DEVICE_ID, uris=[spotify_uri])
                sleep(2)
            except KeyError:
                print("Unkown card presented! First add card association using the add-card.py script.")
                pass

    # If there is an error, skip it and try the code again (i.e. timeout issues, no active device error, etc)
    except Exception as e:
        print(e)
        pass

    finally:
        print("Cleaning up...")
        GPIO.cleanup()
