from atproto import Client
from atproto_core.exceptions import AtProtocolError

handle = 'handle'
appPassword = 'password' # app password can be found at https://bsky.app/settings/app-passwords
readPosts = 10 # the number of latest posts to read
searchTerms = ["comms", "commission", "slots", "ych"]

# log in to bsky
try:
    client = Client()
    client.login(handle, appPassword)
except AtProtocolError:
    print("Error connecting to bsky. Did you add your handle and app password?")
    exit(1)

print("Connected!\n")

# get all follows using cursor
cursor = None
follows = []
while True:
    fetched = client.get_follows(actor=handle,cursor=cursor,limit=100)
    follows = follows + fetched.follows
    if not fetched.cursor:
        break
    cursor = fetched.cursor

print("Searching...\n")
commsList = []
for profile in follows:
    if profile is None:
        continue

    # use handle if display name is empty
    if profile.display_name is None or len(profile.display_name) == 0:
        name = profile.handle
    else:
        name = profile.display_name

    # get description
    desc = ""
    if profile.description is not None and len(profile.description) > 0:
        desc = profile.description

    commsOpen = False
    skipProfile = False
    for s in searchTerms:
        if s in name.lower():
            if "closed" not in name.lower():
                commsOpen = True
        elif s in desc.lower():
            if "closed" not in desc.lower():
                commsOpen = True
            else:
                skipProfile = True # skip this profile so that it doesn't get any posts saying that comms are open
                break

    if skipProfile:
        continue

    # reads the latest posts to see if they mention commissions
    profileFeed = client.get_author_feed(actor=profile.handle,filter='posts_no_replies')
    commPosts = []
    postDates = []
    postIndex = 0 # use an index instead of the limit field to not count reposts
    for feedView in profileFeed.feed:
        if postIndex >= readPosts:
            break

        post = feedView.post
        if post.author.handle != profile.handle: # ignore posts from other users (reposts)
            continue
        if post.record.created_at in postDates: # ignore duplicate posts
            continue
        found = False
        for s in searchTerms:
            if s in post.record.text.lower():
                found = True
        if found:
            if "closed" not in post.record.text.lower():
                commsOpen = True

                # get rkey from uri
                rkeyIndex = post.uri.rfind("/")
                rkey = post.uri[rkeyIndex + 1:]

                commPosts.append("https://bsky.app/profile/" + profile.handle + "/post/" + rkey + "\n" +
                            post.record.text)
                postDates.append(post.record.created_at)
        postIndex += 1

    # if nothing has been found, go to the next profile
    if not commsOpen:
        continue

    # output the info
    print(name + "\n@" +
          profile.handle + "\n" +
          "https://bsky.app/profile/" + profile.handle)
    # output the description
    if len(desc) > 0:
        print("----------------\n" + desc)
    # show the post(s) that it found something in
    if len(commPosts) > 0:
        print("----------------")
        for i in range(len(commPosts)):
            print(postDates[i] + "\n" + commPosts[i])
            if i + 1 < len(commPosts):
                print("- - - - - - - -")
    print("\n================\n")
    commsList.append("https://bsky.app/profile/" + profile.handle)

print("Finished!\nFound:\n")
for profile in commsList:
    print(profile)
