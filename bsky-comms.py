from atproto import Client
from atproto_core.exceptions import AtProtocolError

handle = 'handle'
appPassword = 'password' # app password can be found at https://bsky.app/settings/app-passwords
readPosts = 10 # the number of latest posts to read

# log in to bsky
try:
    client = Client()
    client.login(handle, appPassword)
except AtProtocolError:
    print("Error connecting to bsky. Did you add your handle and app password?")
    exit(1)

print("Connected!\n")

# iterate through follows
follows = client.get_follows(actor=handle).follows
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

    # reads the latest 10 posts to see if they mention commissions
    profileFeed = client.get_author_feed(actor=profile.handle)
    postIndex = 0
    fromPost = ""
    for feedView in profileFeed.feed:
        if postIndex >= readPosts:
            break
        if "comms" in feedView.post.record.text or "commissions" in feedView.post.record.text:
            if "closed" not in feedView.post.record.text:
                commsOpen = True
                feedView.post.record.created_at
                fromPost = feedView.post.record.created_at + "\n" + feedView.post.record.text
        postIndex += 1

    print(profile.display_name + "\n@" +
          profile.handle + "\n" +
          "https://bsky.app/profile/" + profile.handle + "\n"
          "----------------\n" +
          profile.description)
    if len(fromPost) > 0:
        print("----------------\n" +
              fromPost)
    print("\n================\n")
    commsList.append("https://bsky.app/profile/" + profile.handle)

print("Finished!\nFound:\n")
for profile in commsList:
    print(profile)
