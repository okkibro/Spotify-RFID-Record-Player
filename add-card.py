#!/usr/bin/env python3

from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
import os
import sys

load_dotenv()

DEVICE_ID = os.getenv("DEVICE_ID")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

def add_card(reader, sp):
    while True:
        try:
            # Determine type of entry to be added
            type = get_type()

            # Read card and get current song information
            card_id, info = get_info(type, reader, sp)

            # Get correct information based on type
            uri, name = prepare_entry(type, info)

            # Add card and corresponding information to dictionairy
            print(f"The URI for this {type} is: {uri}")
            print(f"The name for this {type} is: {name}")
            print("Creating association in file and resuming...")
            with open("card-dictionairy.csv", "a+") as f:
                f.write(card_id + "," + uri + "," + type + "," + name + "\n")

        finally:
            print("Cleaning up and starting over...")
            GPIO.cleanup()


def prepare_entry(type, info):
    if type == "album":
        uri = info["item"]["album"]["uri"]
        name = info["item"]["album"]["name"]
    elif type == "track":
        uri = info["item"]["uri"]
        name = info["item"]["name"]
    elif type == "artist":
        uri = info["item"]["artists"][0]["uri"]
        name = info["item"]["artists"][0]["name"]
    elif type == "playlist":
        uri = info["context"]["uri"]
        name = "[custom playlist]"

    return uri, name


def get_info(type, reader, sp):
    print(f"Adding {type}! Play {type} on raspotify device and then hold card to reader.")
    reader = SimpleMFRC522()
    card_id = str(reader.read()[0])
    print("The ID for this card is:", card_id)
    info = sp.current_user_playing_track()

    return card_id, info


def get_type():
    type = None
    while type is None:
        raw_type = input("What do you want to add? Type [A] for album, [T] for track, [R] for artist, [P] for playlist, or [Q] to quit: ")
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

    return type


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


def main():
    print("Initializing reader and spotipy...")
    reader, sp = initialize()
    print("Starting add-card loop...")
    add_card(reader, sp)


if __name__ == "__main__":
    main()
