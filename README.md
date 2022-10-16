# Modern Day Record Player

This is a fork of the original modern day record player by [talaexe](https://github.com/talaexe) with some additional features. The original README can be found [here](https://github.com/talaexe/Spotify-RFID-Record-Player/blob/main/README.md).

Additional Python packages required:
- `python-dotenv`

## Changes from original

- Added `add-card.py` script that allows you to easily add "card-track" pairs. First, play the desired track on the `raspotify` device. Next, run the `add-card.py` script and hold an RFID card/tag to the `MFRC522`. The ID of the card and the ID of the currently playing track then get added to a `.csv` file.
- Updated `player.py` script to read from previously mentioned `.csv` file, without the need to update the file for each added song.

## Additional requirements

- Multiple files now require the presence of a `.env` file for the `CLIENT_ID`, `CLIENT_SECRET`, and `DEVICE_ID`. This file *must* be created, simply by adding a file called `.env` to the root of the project, otherwise it will not function. Contents of the file should be 3 lines - one each for the previously mentioned parameters - followed by their respective values.

## TODO:

- Enable better shuffling for artists (now always plays first track first and the other random tracks)
- Increase standard limit of playlist from 100 to infinity [link](https://stackoverflow.com/questions/39086287/spotipy-how-to-read-more-than-100-tracks-from-a-playlist?rq=1)
- Add functionality to skip to next track when scanning currently playing track
- Add functionality to add track to queue instead of skipping currently playing track
- Add start-up script template to enable script to be automatically executed at startup
