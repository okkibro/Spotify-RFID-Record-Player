#!/usr/bin/env python

from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from time import sleep
from dotenv import load_dotenv
import os
import csv
import random

load_dotenv()

DEVICE_ID = os.getenv("DEVICE_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

card_dict = {}

with open('card-dictionairy.csv', mode='r') as f:
    reader = csv.reader(f)
    card_dict = {rows[0]:(rows[1],rows[2]) for rows in reader}

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
                card_info = card_dict[str(card_id)]
                print("Matching card found! Playing...")
                sp.transfer_playback(device_id=DEVICE_ID,force_play=False)
                print(card_info[0])
                if card_info[1] == "track":
                    sp.start_playback(device_id=DEVICE_ID, uris=[card_info[0]])
                elif card_info[1] == "playlist":
                    tracks = sp.playlist_tracks(card_info[0],limit=100)["items"]
                    track_count = len(tracks)
                    random_start_track = random.randint(0,track_count-1)
                    sp.start_playback(device_id=DEVICE_ID,context_uri=card_info[0],offset={"position":random_start_track})
                    sp.shuffle(True,device_id=DEVICE_ID)
                elif card_info[1] == "album":
                    tracks = sp.album_tracks(card_info[0],limit=50)["items"]
                    track_count = len(tracks)
                    random_start_track = random.randint(0,track_count-1)
                    sp.start_playback(device_id=DEVICE_ID,context_uri=card_info[0],offset=random_start_track)
                    sp.shuffle(True,device_id=DEVICE_ID)
                elif card_info[1] == "artist":
                    sp.start_playback(device_id=DEVICE_ID,context_uri=card_info[0])
                    sp.shuffle(True,device_id=DEVICE_ID)
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
