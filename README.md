# Modern Day Record Player

This is a fork of the original modern day record player by [talaexe](https://github.com/talaexe) with some additional features. The original README can be found [here](https://github.com/talaexe/Spotify-RFID-Record-Player/blob/main/README.md).

Additional Python packages required:
- `python-dotenv`

## Changes from original

- Added `add-card.py` script that allows you to easily add "card-track" pairs. First, play the desired track on the `raspotify` device. Next, run the `add-card.py` script and hold an RFID card/tag to the `MFRC522`. The ID of the card and the ID of the currently playing track then get added to a `.csv` file.
- Updated `player.py` script to read from previously mentioned `.csv` file, without the need to update the file for each added song.
- Added functionality for automatically refreshing the `access_token` using the initially created `refresh_token`.

## Additional requirements

- Multiple files now require the presence of a `.env` file for the `CLIENT_ID`, `CLIENT_SECRET`, `GIT_DIR`, and `DEVICE_ID`. This file *must* be created, simply by adding a file called `.env` to the root of the project, otherwise it will not function. Contents of the file should be 4 lines - one each for the previously mentioned parameters - followed by their respective values.

## Running `player.py`

I would recommend using [tmux](https://github.com/tmux/tmux) for running the record player. `tmux` is a terminal multiplexer that allows commands from running in the background and even when disconnecting from the host. `tmux` can easily be installed by running `sudo apt install tmux`. The process of running the record player is now as follows:

1. SSH into `raspotify` device (`ssh [user]@[IP]`)
2. Start new `tmux` sesion (`tmux new -t [name]`)
3. Change directory into root of the project (`cd [dir]`)
4. Start the player (`python3 player.py`)
5. Detach from tmux session (`Ctrl-B + D`)
6. Disconnect SSH connection (`exit`)

A good cheatsheet for `tmux` usage can be found [here]9https://gist.github.com/MohamedAlaa/2961058). The most important command - for when you want to reattach to the previously created `tmux` session - is `tmux attach -t [name]`.

## TODO

- Enable better shuffling for artists (now always plays first track first and the other random tracks).
- Increase standard limit of playlist from 100 to infinity [link](https://stackoverflow.com/questions/39086287/spotipy-how-to-read-more-than-100-tracks-from-a-playlist?rq=1).
- Add functionality to skip to next track (in queue) when currently playing track is scanned again.
- Add functionality to add track to queue instead of skipping currently playing track.
- Add functionality to stop playing after all tracks in queue are gone.
