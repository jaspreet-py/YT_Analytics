import os, requests, json

api_key = os.environ.get("YT_apikey")


# To get all the related channels on the basis of the search query and
# return a dict containing all the channels, with it's title as the
# key containing value for it's thumbnail URL and it's unique
# Channel ID
def get_related_channels(channel_name):
    """
    Takes a Channel Name as parameter and
    gets all the Channel Names, their logo
    thumbnail and their Channel ID from
    Youtube
    """

    base_url = "https://www.googleapis.com/youtube/v3/search"

    params_dict = {
        "q": channel_name,
        "part": "snippet",
        "type": "channel",
        "maxResults": 25,
        "order": "relevance",
        "key": api_key,
    }

    response_object = requests.get(base_url, params=params_dict)
    response = json.loads(response_object.text)
    # print(response_object.content)  # Try when Quota Exceeded

    fin_dict = {}

    try:
        if response["items"] == []:
            return "Sorry! Could not find any channels related to the given keyword. Please try Again!"
        # elif response_object.content
        else:
            for item in response["items"]:
                title = item["snippet"]["title"]
                thumb_url = item["snippet"]["thumbnails"]["default"]["url"]
                channel_id = item["snippet"]["channelId"]

                fin_dict[title] = {"thumbnail": thumb_url, "channel_id": channel_id}
    except Exception as e:
        print(str(e))

    return fin_dict


# Get number of Subscribers for the channels, given it's channel_id and return a
# string containing the number of Subscribers along with additional text for
# easy readability
def get_channel_subs(channel_id):
    """
    Takes a Channel ID as parameter and
    returns their Subscribers
    """

    base_url = "https://www.googleapis.com/youtube/v3/channels"

    params_dict = {
        "id": channel_id,
        "part": "statistics",
        "key": api_key,
    }

    response_object = requests.get(base_url, params=params_dict)
    response = json.loads(response_object.text)

    try:
        subs = int(response["items"][0]["statistics"]["subscriberCount"])
        subs = f"{subs:,}"
        return f"{subs} Subscribers"
    except:
        return "Could not get Subscribers"


# To get basic statistics about a channel, given it's channel ID, and return a
# tuple containing the same
def get_channel_stats(channel_id):
    """
    Returns some basic statistics about the channel (Title, Description, Views, Subscribers, Number of Videos) and the Upload ID
    associated with that channel, which will be used to collect info about all the videos of that Channel

    Required Arguements:
    channel_id: Unique Channel ID associated with a YouTube Channel
    """

    base_channel_url = "https://www.googleapis.com/youtube/v3/channels"

    params_dict = {
        "key": api_key,
        "id": channel_id,
        "part": "contentDetails, statistics, snippet",
    }

    response_obj = requests.get(base_channel_url, params=params_dict)
    response = json.loads(response_obj.text)

    try:
        resp_items = response["items"]

        channel_uid = resp_items[0]["contentDetails"]["relatedPlaylists"]["uploads"]
        channel_name = resp_items[0]["snippet"]["title"]
        channel_desc = resp_items[0]["snippet"]["description"]
        thumb_url = resp_items[0]["snippet"]["thumbnails"]["default"]["url"]
        views = int(resp_items[0]["statistics"]["viewCount"])
        subs = int(resp_items[0]["statistics"]["subscriberCount"])
        num_videos = int(resp_items[0]["statistics"]["videoCount"])

        return (
            channel_uid,
            channel_name,
            channel_desc,
            thumb_url,
            views,
            subs,
            num_videos,
        )
    except Exception as e:
        print(str(e))


# To get all the video IDs(A unique ID associated with each video) associated with a
# a channel and return a list containing the same
def get_vid_ids(upload_id):
    """
    Returns a List of all the video IDs associated with that Channel

    Required Arguements:
    upload_id: The Unique Upload ID of the channel fetched from the previous function (get_channel_stats)
    """

    final_list = []

    base_playlist_url = "https://www.googleapis.com/youtube/v3/playlistItems"
    params_dict = {
        "part": "snippet",
        "playlistId": upload_id,
        "maxResults": 50,
        "key": api_key,
    }

    response_obj = requests.get(base_playlist_url, params=params_dict)
    response = json.loads(response_obj.text)
    resp_items = response["items"]

    for item in resp_items:
        final_list.append(item["snippet"]["resourceId"]["videoId"])

    """
    Since the API can only fetch 50 results per query, it will generate a "nextPageToken" specifying the 
    place to look at for the next 50 results. It will continue to do so until the results left to query 
    are < 50. If the Channel has < 50 videos, it will not generate the "nextPageToken".

    This block checks if there is a "nextPageToken" returned with the query. If so, it executes a while
    loop till the query keeps returning a "nextPageToken". It stops when the token is not returned.
    """
    condition = "nextPageToken" in response
    while condition:
        token = response["nextPageToken"]
        params_dict["pageToken"] = token
        response_obj = requests.get(base_playlist_url, params=params_dict)
        response = json.loads(response_obj.text)
        resp_items = response["items"]

        for item in resp_items:
            final_list.append(item["snippet"]["resourceId"]["videoId"])
        condition = "nextPageToken" in response

    return final_list


# To get statistics for each Individual Video and a list of dicts containing the same
def get_vid_stats(video_ids):
    """
    Returns a list of Lists with each SubList containing the Title, Description, Upload Date, Views, Likes,
    Dislikes, and the number of Comments for a Unique Video

    Required Arguements:
    video_ids: A String (if only 1 Video ID) or a List contiaing Multiple Video IDs
    """

    """
    This while loop is created because at a given time, the API can only fetch data about
    a maximum of 50 videos. So, {x} starts at 0 and increments by 50 each time the loop is
    run. In every loop run, the data about the videos fetched is appended to a list and 
    the loop is run again to fetch the data for the next 50 videos in the {vid_ids} List.
    This keeps on going until x reaches a value >= len(vid_ids), at which point it stops.
    """
    final_list = []

    x = 0
    while x < len(video_ids):
        base_video_url = "https://www.googleapis.com/youtube/v3/videos"
        params_dict = {
            "part": "snippet, statistics",
            "id": video_ids[
                x : x + 50
            ],  # Indexing is done to fetch data for 50 video IDs at a time.
            "key": api_key,
        }

        response_object = requests.get(base_video_url, params=params_dict)
        response = json.loads(response_object.text)
        resp_items = response["items"]

        for item in resp_items:
            title = item["snippet"]["title"]
            # desc = item["snippet"]["description"]
            up_date = item["snippet"]["publishedAt"][:10]
            views = int(item["statistics"]["viewCount"])
            likes = int(item["statistics"]["likeCount"])
            dislikes = int(item["statistics"]["dislikeCount"])
            num_comments = int(item["statistics"]["commentCount"])

            final_list.append([title, up_date, views, likes, dislikes, num_comments])
        x += 50

    return final_list


def get_year_stats(df):
    """
    Returns a dict of number of uploads per year, with the year as
    the key and the number of uploads in that year as it's value

    Required Arguements:
    df: DataFrame from which to get these statistics from, i.e the DataFrame
    containing the complete data about the Channel.
    """

    years = df["Uploaded On"]
    unique_years = list(years.str[:4].unique())

    final_dict = {}

    for year in unique_years:
        mask = df["Uploaded On"].str[:4] == year

        num_videos = int(len(df[mask]))

        final_dict[year] = {
            "Number of Uploads": num_videos,
        }

    return final_dict
