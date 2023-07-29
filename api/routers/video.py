import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.exception import APIException
from db.models.database import get_async_session
from api.schemas.user import GetUserVideosByTagRequest
from api.responses.video import AddNewVideoSchema, ListVideoInfoSchema, DelVideoSchema
from api.schemas.video import AddNewVideoRequest, GetAllVideosByTagRequest, DelVideoVideoRequest, VideoInfo, \
    ListVideoInfo
from utils.determine_tag_id import get_tag_id
from api.dependencies.security import HeaderInitParams
from utils.youtube import get_video_info, get_id_youtube_shorts, create_thumbnails
from db.alchemy.tag import get_tags
from db.alchemy.user import new_user
from db.alchemy.video import new_video, get_video, change_is_active_status, get_all_videos_by_tag, get_user_all_videos, \
    get_user_videos_by_tag

router = APIRouter(prefix="/video", tags=["Клипы"])


async def processing_existing_video(session: AsyncSession, video_id: str, user_id: int):
    """Обработка ситуации с существующей записью клипа"""
    # Обработка ситуации с существующей записью
    video = await get_video(session, video_id)
    if video:
        if video.user_id != user_id:
            raise APIException(5, "video belongs to another user")
        elif video.is_active:
            raise APIException(4, "this clip has already been added")

        # Восстановление видео
        await change_is_active_status(session, video, True)
        raise APIException(6, "video restored")


@router.post("/get-all-videos-by-tag", responses=ListVideoInfoSchema)
async def get_all_videos_by_tag_router(
        _: HeaderInitParams,
        params: GetAllVideosByTagRequest,
        session: AsyncSession = Depends(get_async_session)
):
    """Получение страницы с видео по категории"""
    tag_id, tags_categories = await get_tag_id(session, params.tag)

    videos = await get_all_videos_by_tag(session, tag_id, params.page)
    return ListVideoInfo(
        items=[
            VideoInfo(
                video_id=video.video_id,
                tag=tags_categories.get(video.tag_id, "unknown"),
                date_added=video.date_added,
                owner_id=video.user_id,
                thumbnails=create_thumbnails(video.video_id)
            )
            for video in videos
        ]
    )


@router.post("/get-user-videos-by-tag", responses=ListVideoInfoSchema)
async def get_user_videos_by_tag_router(
        launch_params: HeaderInitParams,
        params: GetUserVideosByTagRequest,
        session: AsyncSession = Depends(get_async_session)
):
    """Видео пользователя по тэгу"""
    tag_id, tags_categories = await get_tag_id(session, params.tag)

    videos = await get_user_videos_by_tag(session, tag_id, launch_params.user_id)
    return ListVideoInfo(
        items=[
            VideoInfo(
                video_id=video.video_id,
                tag=tags_categories.get(video.tag_id, "unknown"),
                date_added=video.date_added,
                owner_id=video.user_id,
                thumbnails=create_thumbnails(video.video_id)
            )
            for video in videos
        ]
    )


@router.post("/get-user-all-videos", responses=ListVideoInfoSchema)
async def get_user_all_videos_router(
        launch_params: HeaderInitParams,
        session: AsyncSession = Depends(get_async_session)
):
    """Получение всех видео пользователя"""
    tags_categories = await get_tags(session)
    videos = await get_user_all_videos(session, launch_params.user_id)
    return ListVideoInfo(
        items=[
            VideoInfo(
                video_id=video.video_id,
                tag=tags_categories.get(video.tag_id, "unknown"),
                date_added=video.date_added,
                owner_id=video.user_id,
                thumbnails=create_thumbnails(video.video_id)
            )
            for video in videos
        ]
    )


@router.post("/add-new-video", responses=AddNewVideoSchema)
async def add_new_video_router(
        launch_param: HeaderInitParams,
        params: AddNewVideoRequest,
        session: AsyncSession = Depends(get_async_session)
):
    """Загрузка нового клипа от имени пользователя"""
    # Проверка валидности ссылки и получение ID клипа
    video_id = get_id_youtube_shorts(params.video_url)
    if not video_id:
        raise APIException(1, "clip link format is invalid")

    # Обработка ситуации с существующей записью
    await processing_existing_video(session, video_id, launch_param.user_id)

    # Получение информации об клипе
    video_info = await get_video_info(video_id)
    if not video_info:
        raise APIException(2, "clip not found")

    # Проверка наличия обязательного тэга приложения
    # todo вернуть
    # if REQUIRED_TAG not in video_info.tags:
    #     raise APIException(3, "the clip is missing a required application tag")

    # Определение тэга видео
    tags_categories = await get_tags(session)
    video_tag = 1

    for tag_id, tag_name in tags_categories.items():
        if tag_name in video_info.tags:
            video_tag = tag_id
            break

    # Создание пользователя при его отсутствии
    await new_user(session, launch_param.user_id)
    # Создание видео
    await new_video(session, video_id, launch_param.user_id, video_tag)

    return VideoInfo(
        video_id=video_id,
        tag=tags_categories[video_tag],
        date_added=datetime.datetime.now(),
        owner_id=launch_param.user_id,
        thumbnails=create_thumbnails(video_id)
    )


@router.post("/del-video", responses=DelVideoSchema)
async def del_video_router(
        launch_param: HeaderInitParams,
        params: DelVideoVideoRequest,
        session: AsyncSession = Depends(get_async_session)
):
    """Удаление клипа от имени пользователя"""
    video = await get_video(session, params.video_id)
    if not video:
        raise APIException(2, "clip not found")

    if video.user_id != launch_param.user_id:
        raise APIException(5, "video belongs to another user")

    return {"success": await change_is_active_status(session, video, False)}
