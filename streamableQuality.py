import praw
import urllib
import requests
import json
import time
import config

print(config.client_id)
reddit = praw.Reddit(client_id=config.client_id, 
    client_secret=config.client_secret, password=config.password, 
    user_agent='streamable quality checker', username=config.username)
streamableAPI = 'https://api.streamable.com/videos/'
seen = []




while(True):
    try:
        nbaPosts = reddit.subreddit('nba').new(limit=25)
        newPosts = []
        for p in nbaPosts:
            if p.id not in seen:
                newPosts.append(p)
                seen.append(p.id)
                if len(seen) > 100:
                    seen.pop(0)

        for post in newPosts[::-1]:
            if 'streamable' in post.url:
                streamableCode = post.url.replace('https://streamable.com/', '')
                streamableCode = streamableCode.replace('http://streamable.com/', '')
                url = streamableAPI + streamableCode
                rawJSON = urllib.request.urlopen(url).read()
                streamableJSON = json.loads(rawJSON.decode('utf-8'))

                framerate = str(streamableJSON['files']['mp4']['framerate'])
                bitrate = str(streamableJSON['files']['mp4']['bitrate'])
                width = str(streamableJSON['files']['mp4']['width'])
                height = str(streamableJSON['files']['mp4']['height'])

                print(post.shortlink + ', ' + post.url + ', ' + framerate + ', ' + bitrate + ', ' + width + ', ' + height)
                if int(bitrate) == 0:
                    print('Failed Checking: ' + post.shortlink + ', ' + post.url)
                    seen.remove(post.id)
                elif int(framerate) < 24 or int(bitrate) <= 950000 or int(width) < 1000:
                    if post.approved_by == None and len(post.report_reasons) == 0: 
                        reportReason = 'Low Quality - ' + width + 'x' + height + ', ' + str(int(round(int(bitrate), -5)/1000)) + 'kbps, ' + framerate + 'fps'
                        print(reportReason)
                        post.report(reportReason)


        time.sleep(30)
    except Exception as e:
        print('exception hit: ' + str(e))
        time.sleep(120)
