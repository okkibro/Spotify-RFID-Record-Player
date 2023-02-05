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
import requests
import urllib3

load_dotenv()

DEVICE_ID = os.getenv("DEVICE_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
GIT_DIR = os.getenv("GIT_DIR")

def player(card_dict, reader, auth_manager, sp, queue, skip):
    while True:
        print("Waiting for record scan...")
        card_id = reader.read()[0]
        print("Read succesful! Finding track corresponding to card...")
        card_info = None

        sleep(1)

        try:
            card_info = card_dict[str(card_id)]
            print("Matching card found! Playing...")

        except KeyError:
            print("Unknown card presented! First add card association using the add-card.py script.")
            sleep(2)
            pass

        if card_info is not None:
            auth_manager, sp = refresh_spotify(auth_manager, sp)

            try:
                currently_playing = sp.currently_playing()
                is_playing = get_is_playing(currently_playing)
                is_same_song = check_same_song(currently_playing, card_info)
                devices = sp.devices()
                is_jukebox_active = is_jukebox_active_device(devices)

            except (ConnectionResetError, requests.exceptions.ConnectionError, urllib3.exceptions.ProtocolError) as e:
                print("Connection was temporarily reset! Attempting to reconnect and restart...")
                auth_manager, sp = refresh_spotify(auth_manager, sp)
                pass

            if is_jukebox_active is False:
                sp.transfer_playback(device_id=DEVICE_ID,force_play=True)

            if is_playing and queue and not is_same_song:
                print("Adding to queue!")
                add_to_queue(sp, card_info, is_playing)
            elif is_playing and is_same_song and skip:
                print("Skipping item!")
                skip_item(sp)
            else:
                print("Playing item!")
                play_item(sp, card_info)


def perform_premptive_skip(currently_playing):
    if currently_playing is None:
        return False
    elif currently_playing["progress_ms"] == 0:
        return True
    else:
        return False


def get_is_playing(currently_playing):
    if currently_playing is None:
        return False
    elif currently_playing["is_playing"] is True:
        return True
    elif currently_playing["is_playing"] is False and currently_playing["progress_ms"] > 0:
        return True
    else:
        return False


def is_jukebox_active_device(devices):
    active_device = next((item for item in devices['devices'] if item["is_active"] == True), None)

    if active_device is None:
        return False
    if active_device['id'] == DEVICE_ID:
        return True
    else:
        return False


def check_same_song(currently_playing, card_info):
    if currently_playing is None:
        return False
    elif currently_playing['is_playing'] is False:
        return False
    elif currently_playing["item"]["uri"] == card_info[0]:
        return True
    else:
        return False


def add_to_queue(sp, card_info, is_playing):
    sp.add_to_queue(device_id=DEVICE_ID, uri=card_info[0])

    if not is_playing:
        sp.start_playback()


def skip_item(sp):
    sp.next_track(device_id=DEVICE_ID)


def play_item(sp, card_info):
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
        redirect_uri="http://localhost:8080",
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
        print("Refreshing token!")

        try:
            token_info = auth_manager.refresh_access_token(token_info["refresh_token"])
            token = token_info["access_token"]
            sp = spotipy.Spotify(auth=token)

        except (ConnectionResetError, requests.exceptions.ConnectionError, urllib3.exceptions.ProtocolError) as e:
            print("Something went wrong with the connection! Trying again...")
            pass

    return auth_manager, sp


def read_dictionairy(file_location):
    card_dict = {}

    with open(file_location, mode="r") as f:
        reader = csv.reader(f)
        card_dict = {rows[0]:(rows[1],rows[2]) for rows in reader}

    return card_dict


def main(queue=False, skip=False):
    print("Reading card dictionairy...")
    card_dict = read_dictionairy(GIT_DIR + '/card-dictionairy.csv')
    print("Initializing reader...")
    reader = create_reader()
    print("Initializing spotify...")
    auth_manager, sp = create_spotify()
    print("Starting player...")
    player(card_dict, reader, auth_manager, sp, queue, skip)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Control Spotify Connect device using MFRC522, RFID tags, and the Spotify API")
    parser.add_argument("-q", "--queue", action="store_true", help="Add song to queue when song is already playing, instead of skipping currently playing song")
    parser.add_argument("-s", "--skip", action="store_true", help="If the currently playing song is scanned again, the next song in the queue (if present) will be played")
    args = parser.parse_args()
    main(args.queue, args.skip)
