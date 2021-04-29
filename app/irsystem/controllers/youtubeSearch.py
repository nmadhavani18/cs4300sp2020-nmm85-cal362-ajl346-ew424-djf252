# -*- coding: utf-8 -*-

# Sample Python code for youtube.search.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/guides/code_samples#python

import io
import os
import sys
import json
import pprint

import googleapiclient.discovery

def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = "AIzaSyBv8cM9jRZfZ2QmVcnSqMunqzIFr4PwZxg"

    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = DEVELOPER_KEY)

    # requests return json files for each search query
    request = youtube.search().list(
        part="snippet",
        q="tom brady highlights"
    )

    request2 = youtube.search().list(
        part="snippet",
        q="peyton manning highlights"
    )

    request3 = youtube.search().list(
        part="snippet",
        q="aaron rodgers highlights"
    )

    request4 = youtube.search().list(
        part="snippet",
        q="eli manning highlights"
    )

    request5 = youtube.search().list(
        part="snippet",
        q="john elway highlights"
    )

    # responses are json files in the format of response.json
    # 5 responses, 1 for each output
    response = request.execute()
    responseJson = json.dumps(response)

    response2 = request2.execute()
    responseJson2 = json.dumps(response2)

    response3 = request3.execute()
    responseJson3 = json.dumps(response3)

    response4 = request4.execute()
    responseJson4 = json.dumps(response4)

    response5 = request5.execute()
    responseJson5 = json.dumps(response5)

    # Outputs are arrays of tuples with (thumbnail URL, video URL)
    # Each output array is of length 5 (5 thumbnails per player)
    # There are 5 output arrays (5 players in the output)
    output1 = []
    output2 = []
    output3 = []
    output4 = []
    output5 = []
    for i in range(5):
        output1 += [(response["items"][i]["snippet"]["thumbnails"]["high"]["url"],
            "https://www.youtube.com/watch?v=" + response["items"][i]["id"]["videoId"])]
        output2 += [(response2["items"][i]["snippet"]["thumbnails"]["high"]["url"],
            "https://www.youtube.com/watch?v=" + response2["items"][i]["id"]["videoId"])]
        output3 += [(response3["items"][i]["snippet"]["thumbnails"]["high"]["url"],
            "https://www.youtube.com/watch?v=" + response3["items"][i]["id"]["videoId"])]
        output4 += [(response4["items"][i]["snippet"]["thumbnails"]["high"]["url"],
            "https://www.youtube.com/watch?v=" + response4["items"][i]["id"]["videoId"])]
        output5 += [(response5["items"][i]["snippet"]["thumbnails"]["high"]["url"],
            "https://www.youtube.com/watch?v=" + response5["items"][i]["id"]["videoId"])]

    print(output1)
    return (output1, output2, output3, output4, output5)

if __name__ == "__main__":
    main()
