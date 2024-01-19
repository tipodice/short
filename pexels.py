import requests
import random
import os
from log import logger
from utils import get_duration
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())

API_KEY = os.environ.get('API_KEY')
HEADERS = {"Authorization": API_KEY}


def download_videos(topic, output_folder, total_pages):
    """
    Download videos related to the given topic until the total duration exceeds the duration of an audio file.

    Args:
        topic (str): The topic for which videos are to be downloaded.
        output_folder (str): The folder where downloaded videos will be saved.
        total_pages (int): The total number of pages to fetch video IDs.

    Raises:
        Exception: If an error occurs during the video download process.

    Returns:
        None
    """
    ids_list = fetch_video_ids(topic, total_pages=total_pages)
    audio_duration = get_duration('tmp/t2s.wav')
    video_duration = 0
    downloaded_ids = []

    while video_duration < audio_duration:
        try:
            current_video_id = random.choice(ids_list)
            if current_video_id not in downloaded_ids:
                try:
                    output_video = output_folder + f'{current_video_id}.mp4'
                    download_pexels_video(current_video_id, output_video)
                    video_duration += get_duration(output_video)
                    downloaded_ids.append(current_video_id)
                except Exception as e:
                    # Log or handle the exception appropriately
                    pass
        except Exception as e:
            # Log or handle the exception appropriately
            raise e

def download(url, output_path):
    """
    Download content from a given URL and save it to the specified output path.

    Args:
        url (str): The URL of the content to download.
        output_path (str): The path to save the downloaded content.

    Raises:
        Exception: If there is an issue with the download.
    """
    try:
        with open(output_path, "wb") as f:
            f.write(requests.get(url, timeout=15).content)
    except Exception as e:
        logger.error(f'Failed to download content from {url}: {e}')
        raise e

def download_pexels_video(media_id, output_path, quality='hd'):
    """
    Download a Pexels video with a given media ID and save it to the specified output path.

    Args:
        media_id (int): The ID of the Pexels video.
        output_path (str): The path to save the downloaded video.
        quality (str): The quality of the video, either 'hd' (1920) or 'sd' (1280).

    Raises:
        ValueError: If the specified quality is not supported or there is no video available for the given ID.
        Exception: If there is an issue with the download.
    """
    try:
        if quality == 'hd':
            quality = 1920
        elif quality == 'sd':
            quality = 1280
        else:
            raise ValueError('Quality provided is not supported. Use quality="hd" or quality="sd"')

        url = f"https://api.pexels.com/videos/videos/{media_id}"
        response = requests.get(url, headers=HEADERS)
        link = None

        if response.status_code == 200:
            data = response.json()
            videos = data.get("video_files")

            try:
                print('')
                selected_video = next(filter(lambda x: x['width'] == quality, videos))
                link = selected_video.get('link')
            except Exception as e:
                raise ValueError(f'There is no {quality} video available for id {media_id}, trying another id...')

            download(link, output_path)
            logger.info(f'Video id {media_id} downloaded successfully')
            return output_path
        else:
            raise ValueError(f'Unable to get video with status code {response.status_code} and response {response.text}')
    except Exception as e:
        logger.error(f'Failed to download Pexels video with id {media_id}: {e}')
        raise e

def fetch_video_ids(topic, per_page=80, total_pages=100):
    """
    Fetch video IDs for a given topic from the Pexels API.

    Args:
        topic (str): The topic to search for.
        per_page (int, optional): Number of videos per page (max 80). Defaults to 80.
        total_pages (int, optional): Total number of pages to fetch. Defaults to 100.

    Returns:
        list: A list of video IDs.

    Raises:
        ValueError: If per_page exceeds the maximum allowed value.
        requests.exceptions.RequestException: If there is an issue with the HTTP request.
    """
    try:
        if per_page > 80:
            raise ValueError('Max per_page parameter is 80')

        url = "https://api.pexels.com/v1/videos/search"
        all_ids = []

        for _ in range(total_pages):
            page = random.randint(1, total_pages)
            logger.info(f'Fetching IDs from page {page}')
            query_params = {"query": topic, "per_page": per_page, "page": page}

            response = requests.get(url, params=query_params, headers=HEADERS)

            if response.status_code == 200:
                data = response.json()
                all_media = data.get('videos', [])

                if all_media:
                    all_ids.extend(media['id'] for media in all_media)
                    return all_ids

    except requests.exceptions.RequestException as e:
        logger.error(f'Failed to fetch video IDs for topic {topic}: {e}')
        raise e
    except Exception as e:
        logger.error(f'An unexpected error occurred: {e}')
        raise e

