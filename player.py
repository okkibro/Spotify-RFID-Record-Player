#!/usr/bin/env python3

from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from time import sleep
from dotenv import load_dotenv
import os
import csv
import random
import argparse

load_dotenv()

DEVICE_ID = os.getenv("DEVICE_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

def player(reader, sp, card_dict):
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
            print("Unknown card presented! First add card association using the add-card.py script.")
            pass

def initialize():
    try:
        reader = SimpleMFRC522()
        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri="http://localhost:8080",
            scope="""
                user-read-playback-state,
                user-modify-playback-state,
                user-read-currently-playing,
                playlist-modify-private,
                playlist-read-private
                """
            )
        )

    except Exception as e:
        print(e)
        pass

    finally:
        print("Cleaning up...")
        GPIO.cleanup()

    return reader, sp

def read_dictionairy(file_location):
    card_dict = {}

    with open(file_location, mode='r') as f:
        reader = csv.reader(f)
        card_dict = {rows[0]:(rows[1],rows[2]) for rows in reader}

    return card_dict

def main(queue=False):
    print("Reading card dictionairy...")
    card_dict = read_dictionairy('/home/omuller/Spotify-RFID-Record-Player/card-dictionairy.csv')
    print("Initializing reader and spotipy...")
    reader, sp = initialize()
    print("Starting player...")
    player(reader, sp, card_dict)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Control Spotify Connect device using MFRC522, RFID tags, and the Spotify API')
    parser.add_argument('-q', '--queue', action='store_true', help='Add song to queue when song is already playing, instead of skipping currently playing song')
    args = parser.parse_args()
    main(args.queue)
