# your user handle used to log in to bsky
myHandle = 'handle'
# your app password - can be found at https://bsky.app/settings/app-passwords
appPassword = 'password'
# what terms to search for in posts and descriptions
searchTerms = ["comms", "commission", "slots", "ych"]
# the number of latest posts to read
readPosts = 10
# the max number of days to search back through. < 0 means no time limit
searchDays = 10
# handles included here will be excluded from the results
excludeHandles = []

# ================================

from atproto import Client
from atproto_core.exceptions import AtProtocolError
from atproto_client.models.app.bsky.feed.defs import ReasonRepost
from atproto_client.exceptions import BadRequestError
from datetime import datetime

# log in to bsky
try:
    client = Client()
    client.login(myHandle, appPassword)
except AtProtocolError:
    print("Error connecting to bsky. Did you add your handle and app password?")
    exit(1)

print("Connected!\n")

# get all follows using cursor
cursor = None
follows = []
while True:
    fetched = client.get_follows(actor=myHandle, cursor=cursor, limit=100)
    follows = follows + fetched.follows
    if not fetched.cursor:
        break
    cursor = fetched.cursor

print("Searching...\n")
commsList = []
for profile in follows:
    if profile is None:
        continue

    # use did if handle is invalid
    if profile.handle == "handle.invalid":
        profileHandle = profile.did
    else:
        profileHandle = profile.handle

    # skip excluded handles
    if profile.handle in excludeHandles:
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
    try:
        profileFeed = client.get_author_feed(actor=profileHandle,filter='posts_no_replies')
    except BadRequestError:
        print("Error fetching feed of user: " + profileHandle)
        continue

    commPosts = []
    postDates = []
    postIndex = 0 # use an index instead of the limit field to not count reposts
    for feedView in profileFeed.feed:
        if postIndex >= readPosts:
            break

        post = feedView.post
        if feedView.reason != ReasonRepost: # don't check the date for reposts
            if searchDays >= 0:
                # get the timestamp - [year]-[month]-[date]T[hour]-[minute]-[second].[microseconds][TZ]
                # TZ can be 'Z' or '±HH:MM'. microseconds are optional
                timestr = post.record.created_at
                if timestr.find('Z') != -1:
                    try:
                        parseFormat = '%Y-%m-%dT%H:%M:%SZ'
                        timestamp = datetime.strptime(timestr, parseFormat)
                    except ValueError:
                        parseFormat = '%Y-%m-%dT%H:%M:%S.%fZ'
                        timestamp = datetime.strptime(timestr, parseFormat)
                else:
                    try:
                        parseFormat = '%Y-%m-%dT%H:%M:%S%z'
                        timestamp = datetime.strptime(timestr, parseFormat)
                    except ValueError:
                        parseFormat = '%Y-%m-%dT%H:%M:%S.%f%z'
                        timestamp = datetime.strptime(timestr, parseFormat)
                # convert the post timestamp to the local timezone
                localisedTimestamp = timestamp.astimezone(datetime.now().tzinfo).replace(tzinfo=datetime.now().tzinfo)
                diff = datetime.now() - localisedTimestamp
                if diff.days > searchDays: # ignore posts older than searchDays
                    break
        if post.author.handle != profileHandle: # ignore posts from other users (reposts)
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
                rkey = post.uri[post.uri.rfind("/") + 1:]

                commPosts.append("https://bsky.app/profile/" + profileHandle + "/post/" + rkey + "\n" +
                            post.record.text)
                postDates.append(post.record.created_at)
        postIndex += 1

    # if nothing has been found, go to the next profile
    if not commsOpen:
        continue

    # output the info
    print(name + "\n@" +
          profileHandle + "\n" +
          "https://bsky.app/profile/" + profileHandle)
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
    commsList.append("https://bsky.app/profile/" + profileHandle)

print("Finished!\nFound:\n")
for profile in commsList:
    print(profile)
