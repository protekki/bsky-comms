from atproto import Client
from atproto_core.exceptions import AtProtocolError

handle = 'handle'
appPassword = 'password'
# app password can be found at https://bsky.app/settings/app-passwords

# log in to bsky
try:
    client = Client()
    client.login(handle, appPassword)
except AtProtocolError:
    print("Error connecting to bsky. Did you add your handle and app password?")
    exit(1)

print("Connected!\n")

# iterate through follows
follows = client.get_follows(handle, None, None).follows
print("Searching for \"comms\"/\"commissions\"...\n")
commsList = []
for profile in follows:
    # check if profile name mentions comms
    name = profile.display_name.lower()
    # check if profile description mentions comms
    desc = profile.description.lower()
    commsOpen = False
    if "comms" in name or "commissions" in name:
        if "closed" not in name:
            commsOpen = True
    elif "comms" in desc or "commissions" in desc:
        if "closed" not in desc:
            commsOpen = True
        else:
            commsOpen = False
    if not commsOpen:
        continue

    print(profile.display_name + "\n@" +
          profile.handle + "\n" +
          "https://bsky.app/profile/" + profile.handle + "\n"
          "----------------\n" +
          profile.description + "\n\n" +
          "================\n")
    commsList.append("https://bsky.app/profile/" + profile.handle)

print("Finished!\nFound:\n")
for profile in commsList:
    print(profile)