import re
from dataclasses import dataclass
from urllib.parse import urlparse
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import YOUTUBE_API_KEYS
from utils.infiniteiterator import InfiniteListIterator

API_KEY = 'your_api_key'
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

FORMAT_URL_THUMBNAIL = "https://i.ytimg.com/vi/%s/%s.jpg"
THUMBNAIL_FORMATS = ["default", "hqdefault", "maxresdefault", "mqdefault", "sddefault"]

get_next_api_token = InfiniteListIterator(YOUTUBE_API_KEYS)


@dataclass
class VideoInfo:
    video_id: str
    likes: int
    tags: list[str]


def get_id_youtube_shorts(video_url) -> str | None:
    """Получение ID видео из ссылки, с проверкой валидности ссылки"""
    parsed_url = urlparse(video_url)

    if "youtube" not in parsed_url.hostname.lower():
        return None

    if not parsed_url.path.startswith("/shorts/"):
        return None

    shorts_id = parsed_url.path.replace("/shorts/", "")

    if len(shorts_id) != 11:
        return None

    return shorts_id


def extract_hashtags(text: str) -> list[str]:
    """Извлечение всех хэштегов из текса"""
    hashtags = re.findall(r'#(\w+)', text)
    return [i.lower() for i in hashtags]


def create_thumbnails(video_id: str) -> list[str]:
    """Создание списка ссылок для обложки"""
    return [
        FORMAT_URL_THUMBNAIL % (video_id, f) for f in THUMBNAIL_FORMATS
    ]


async def get_video_info(video_id) -> VideoInfo | None:
    """Получение информации о видео"""
    youtube = build(API_SERVICE_NAME, API_VERSION, developerKey=anext(get_next_api_token))

    try:
        v_response = youtube.videos().list(
            part='snippet,statistics',
            id=video_id
        ).execute()
    except (HttpError, Exception) as e:
        # todo добавить логирование ошибки
        return None

    if 'items' not in v_response or not len(v_response['items']):
        return None

    video_item = v_response['items'][0]
    snippet = video_item['snippet']
    statistics = video_item['statistics']

    likes = int(statistics['likeCount']) if 'likeCount' in statistics else 0
    tags = extract_hashtags(snippet['title']) if 'title' in snippet else []

    return VideoInfo(video_id=video_id, likes=likes, tags=tags)
