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
print("Searching...\n")
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
            continue
            # skip this profile so that it doesn't get any posts saying that comms are open

    # reads the latest posts to see if they mention commissions
    profileFeed = client.get_author_feed(actor=profile.handle,filter='posts_no_replies')
    fromPost = ""
    postIndex = 0 # use an index instead of the limit field to not count reposts
    for feedView in profileFeed.feed:
        if postIndex >= readPosts:
            break
        if feedView.post.author.handle != profile.handle:
            continue
        if "comms" in feedView.post.record.text or "commissions" in feedView.post.record.text:
            if "closed" not in feedView.post.record.text:
                commsOpen = True
                if len(fromPost) > 0:
                    fromPost += "\n- - - - - - - -\n"

                # get rkey from uri
                rkeyIndex = feedView.post.uri.rfind("/")
                rkey = feedView.post.uri[rkeyIndex + 1:]

                fromPost = (feedView.post.record.created_at + "\n" +
                            "https://bsky.app/profile/" + profile.handle + "/post/" + rkey + "\n" +
                            feedView.post.record.text)
        postIndex += 1

    # if nothing has been found, go to the next profile
    if not commsOpen:
        continue

    # output the info
    print(profile.display_name + "\n@" +
          profile.handle + "\n" +
          "https://bsky.app/profile/" + profile.handle + "\n"
          "----------------\n" +
          profile.description)
    # show the post that it found something in
    if len(fromPost) > 0:
        print("----------------\n" + fromPost)
    print("\n================\n")
    commsList.append("https://bsky.app/profile/" + profile.handle)

print("Finished!\nFound:\n")
for profile in commsList:
    print(profile)
