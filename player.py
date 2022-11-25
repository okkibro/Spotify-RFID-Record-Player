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
GIT_DIR = os.getenv("GIT_DIR")

def player(card_dict, reader, auth_manager, sp):
    while True:
        print("Waiting for record scan...")
        card_id = reader.read()[0]
        print("Read succesful! Finding track corresponding to card...")
        try:
            card_info = card_dict[str(card_id)]
            print("Matching card found! Playing...")
            auth_manager, sp = refresh_spotify(auth_manager, sp)
            sp.transfer_playback(device_id=DEVICE_ID,force_play=False)
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
            sleep(1)

        except KeyError:
            print("Unknown card presented! First add card association using the add-card.py script.")
            pass


def create_reader():
    try:
        reader = SimpleMFRC522()

    except Exception as e:
        print(e)
        pass

    finally:
        print("Cleaning up...")
        GPIO.cleanup()

    return reader


def create_spotify():
    auth_manager = SpotifyOAuth(
        open_browser=False,
        redirect_uri='http://localhost:8080',
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scope="""
            user-read-playback-state,
            user-modify-playback-state,
            user-read-currently-playing,
            playlist-modify-private,
            playlist-read-private
            """
    )

    sp = spotipy.Spotify(auth_manager=auth_manager)

    return auth_manager, sp


def refresh_spotify(auth_manager, sp):
    token_info = auth_manager.cache_handler.get_cached_token()

    if auth_manager.is_token_expired(token_info):
        token_info = auth_manager.refresh_access_token(token_info['refresh_token'])
        token = token_info['access_token']
        sp = spotipy.Spotify(auth=token)

    return auth_manager, sp


def read_dictionairy(file_location):
    card_dict = {}

    with open(file_location, mode='r') as f:
        reader = csv.reader(f)
        card_dict = {rows[0]:(rows[1],rows[2]) for rows in reader}

    return card_dict


def main(queue=False):
    print("Reading card dictionairy...")
    card_dict = read_dictionairy(GIT_DIR + '/card-dictionairy.csv')
    print("Initializing reader...")
    reader = create_reader()
    print("Initializing spotify...")
    auth_manager, sp = create_spotify()
    print("Starting player...")
    player(card_dict, reader, auth_manager, sp)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Control Spotify Connect device using MFRC522, RFID tags, and the Spotify API')
    parser.add_argument('-q', '--queue', action='store_true', help='Add song to queue when song is already playing, instead of skipping currently playing song')
    args = parser.parse_args()
    main(args.queue)
