import logging
from pprint import pformat
import sys
import json
from config import config
import requests

def fetch_playlist_items_page(googleApiKey, playlistId, pageToken=None):
    response = requests.get("https://www.googleapis.com/youtube/v3/playlistItems",
                            params={
                                "key": googleApiKey,
                                "playlistId": playlistId,
                                "part": "contentDetails",
                                "pageToken":pageToken
                            })
    payload = json.loads(response.text)

    # logging.debug("GOT %s", payload)

    return payload

def fetch_videos_page(googleApiKey, videoId, pageToken=None):
    response = requests.get("https://www.googleapis.com/youtube/v3/videos",
                            params={
                                "key": googleApiKey,
                                "id": videoId,
                                "part": "snippet",
                                "pageToken":pageToken
                            })
    payload = json.loads(response.text)

    # logging.debug("GOT %s", payload)

    return payload

def fetch_videos(googleApiKey, playlistId, pageToken=None):
    # Fetch one page
    payload = fetch_videos_page(googleApiKey,playlistId, pageToken)

    # Serve up items from that page
    yield from payload["items"]

    nextPageToken = payload.get("nextPageToken")

    # If there's another page
    if nextPageToken:
        yield from fetch_videos(googleApiKey, playlistId, nextPageToken)

def fetch_playlist_items(googleApiKey, playlistId, pageToken=None):
    # Fetch one page
    payload = fetch_playlist_items_page(googleApiKey,playlistId, pageToken)

    # Serve up items from that page
    yield from payload["items"]

    nextPageToken = payload.get("nextPageToken")

    # If there's another page
    if nextPageToken:
        yield from fetch_playlist_items(googleApiKey, playlistId, nextPageToken)

def summarizeVideo(video):
    return {
        "videoId": video["id"],
        "title": video["snippet"]["title"],
        "views": video["statistics"].get("viewCount",0),
        "likes": video["statistics"].get("likeCount",0),
        "comments": video["statistics"].get("commentCount",0)
    }


def main():
    logging.info("START")
    googleApiKey = config["GOOGLE_API_KEY"]
    playlistId = config["YOUTUBE_PLAYLIST_ID"]

    for videoItem in fetch_playlist_items(googleApiKey, playlistId):
        videoId = videoItem["contentDetails"]["videoId"]
        for video in fetch_videos(googleApiKey, videoId):
            logging.info("GOT %s", pformat(video))

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    sys.exit(main())