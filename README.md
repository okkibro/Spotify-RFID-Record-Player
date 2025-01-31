# Modern Day Record Player

This is a fork of the original modern day record player by [talaexe](https://github.com/talaexe) with some additional features. The original README can be found [here](https://github.com/talaexe/Spotify-RFID-Record-Player/blob/main/README.md).

Additional Python packages required:
- `python-dotenv`

## Changes from original

- Added `add-card.py` script that allows you to easily add "card-track" pairs. First, play the desired track on the `raspotify` device. Next, run the `add-card.py` script and hold an RFID card/tag to the `MFRC522`. The ID of the card and the ID of the currently playing track then get added to a `.csv` file.
- Updated `player.py` script to read from previously mentioned `.csv` file, without the need to update the file for each added song.
- Added functionality for automatically refreshing the `access_token` using the initially created `refresh_token`.
- Added ability to add songs to queue or skip the currently playing song.

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

A good cheatsheet for `tmux` usage can be found [here](https://gist.github.com/MohamedAlaa/2961058). The most important command - for when you want to reattach to the previously created `tmux` session - is `tmux attach -t [name]`.

## TODO

- Enable better shuffling for artists (now always plays first track first and the other random tracks).
- Increase standard limit of playlist from 100 to infinity [link](https://stackoverflow.com/questions/39086287/spotipy-how-to-read-more-than-100-tracks-from-a-playlist?rq=1).

## Known issues

- When first booting up the Raspberry Pi and starting the `player.py` script, you will always get an `HTTP Error for PUT to https://api.spotify.com/v1/me/player with Params: {} returned 404 due to Device not found` error when scanning the first RFID tag/card. This is always the case, since, when a new device is added to the network (i.e.: when you boot the Raspberry Pi and the `raspotify` Spotify Connect device is initialized by running the `player.py` script) it is not visible. The Spotify Developer Guide also mentions [this](https://developer.spotify.com/documentation/web-api/guides/using-connect-web-api/#devices-not-appearing-on-device-list) (in this case it's for the Connect Web API, but I'm guessing the reason is similar). The only way to fix this (maybe there are other ways, but this is the consistent way I fixed it) is by first manually connecting to the `raspotify` device with your phone/desktop. You don't even have to play a song with it, but just the act of connecting with it, will make the device discoverable and the `player.py` script work. You will not have to do this every time you run the `player.py` script, just the first time after booting the Raspberry Pi.

## How to fix autoplay "feature"

- `raspotify` uses [librespot](https://github.com/librespot-org/librespot) as its back-end client library for Spotify. `librespot` has a bunch of [options](https://github.com/librespot-org/librespot/wiki/Options), one of which is `autoplay`. Normally, when using `librespot` as stand-alone software, autoplay is enabled by handing it as a flag, but for `raspotify` this is done in the form of a config file located at `/etc/raspotify/conf`. This feature is enabled by default, which means that when you scan a single RFID card, it will *always* start playing similar songs, even if you want to play just the song you just scanned. This feature can be disabled by going to the aforementioned config file, commenting out the line called `LIBRESPOT_AUTOPLAY=` by placing a `#` in front of it, and then running `sudo systemctl restart raspotify`.
