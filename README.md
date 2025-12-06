# Requirements
- Python 3.8 or later
- `atproto` package

# Usage
1. Edit bsky-comms.py and set `myHandle` and `appPassword` to your username and app password respectively (this can be found at https://bsky.app/settings/app-passwords)

2. Run bsky-comms.py with python

# Options
The variables at the top of the file are options, edit them if desired.

If you want to output to a file instead of the console, set `createFile` to `True`. File name defaults to "bsky-comms_[date]". For a custom name, edit `outFileName` or pass a file name via argument (`python3 bsky-comms.py filename`)

# Compatibility
This has only been tested on Linux, but it should work on other platforms.
