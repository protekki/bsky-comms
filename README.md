# Requirements
- Python 3.8 or later
- `atproto` pip package

# Usage
1. Edit bsky-comms.py and set `myHandle` and `appPassword` to your username and app password respectively (this can be found at https://bsky.app/settings/app-passwords)

2. Run bsky-comms.py with python

# Options
The variables at the top of the file are options, edit them if desired.

- `searchTerms`: list of strings to search for. Must be in lower case, otherwise they will fail to match (posts are converted to lower case in case they are upper or mixed case)
- `negativeTerms`: list of strings that we don't want. When found in a display mame or bio, the profile is skipped. When found in a post in combination with a search term, the post is skipped. E.g. if one search term is 'comm' and a negative term is 'closed', then a post including 'comms closed' would be a match.
- `readPosts`: Integer. Number of posts to read searching for `searchTerms`.
- `searchDays`: Integer. When finding a post older than this number of days ago, stop reading posts.
- `excludeHandles`: list of handles that will be ignored
- `createFile`: Boolean. Whether or not a file is created. If false, outputs to terminal.
- `outFileName`: String. The name of the file to be created. If empty, uses the current date and time.
- `dateName`: Boolean. Adds the current date and time to the file name. Has no effect if `outFileName` not set.
- `showImageCount`: Boolean. If enabled, says what embeds (if any) are included in a post.

### Notes
- Reposts (not quote posts) are ignored. They don't get scanned for `searchTerms`, and don't effect `readPosts` or `searchDays`.
- AI was not used to make this script :)
