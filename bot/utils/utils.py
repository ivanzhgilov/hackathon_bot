import asyncio
import logging
import re
from typing import Literal

import aiohttp
import argon2
from aiogram import Bot
from geopy.adapters import AioHTTPAdapter
from geopy.distance import distance
from geopy.geocoders import Nominatim
from sqlalchemy import select

from core.text import get_point_text
from models import User
from utils.database import db_async_session_manager


async def count_active_users(commands):
    lst = []
    c = 0
    for command in commands:
        if command.chat_id not in lst:
            c += 1
            lst.append(command.chat_id)
    return c


async def command_usage(commands):
    point_request = 0
    eco_bank = 0
    points_of_city = 0
    articles = 0
    useful_links = 0
    for command in commands:
        if command.name == "eco_bank":
            eco_bank += 1
        elif command.name == "points_of_city":
            points_of_city += 1
        elif command.name == "articles":
            articles += 1
        elif command.name == "useful_links":
            useful_links += 1
    return {"point_request": point_request,
            "eco_bank": eco_bank,
            "points_of_city": points_of_city,
            "articles": articles,
            "useful_links": useful_links}


async def send_message_to_all_users(bot: Bot, message):
    text = f'{message[0]}\n{message[1]}'
    async with db_async_session_manager() as session:
        users = await session.execute(select(User))
    for user in users.scalars().all():
        await bot.send_message(chat_id=user.chat_id, text=text)


async def get_poster(last_post):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        token = "95dee14b95dee14b95dee14b0f96c6c94b995de95dee14bf3f0b14bc725dd7241b71737"
        url = f"https://api.vk.com/method/wall.get?access_token={token}&v=5.199&domain=eco4u2&count=1"
        async with session.get(url) as post:
            data = await post.json()

            post_text = data["response"]["items"][0]["text"]
            link = "https://vk.com/eco4u2"

            if (post_text, link) != last_post:
                return post_text, link
            else:
                return None


async def get_coordinates_by_address(address: str, country_code: str = 'RU') -> tuple:
    url = f"https://nominatim.openstreetmap.org/search?q={address},{country_code}&format=json&limit=1"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                return None, None

            data = await response.json()
            if not data:
                return None, None

            lon, lat = data[0]["lon"], data[0]["lat"]
            return float(lat), float(lon)


def hash_password(password: str) -> str:
    argon2_hasher = argon2.PasswordHasher()
    return argon2_hasher.hash(password)


def check_password(hashed_password: str, password: str) -> bool:
    argon2_hasher = argon2.PasswordHasher()
    return argon2_hasher.verify(hashed_password, password)


async def get_city(lat, lon):
    async with Nominatim(
            user_agent="my-mput-srr",
            adapter_factory=AioHTTPAdapter,
    ) as geolocator:
        location = await geolocator.reverse(f"{lat}, {lon}")
        if location.raw["address"].get("town") == "Белый Яр":
            return "Белый Яр"
        return location.raw["address"].get("city", "")


def setup_logging(level: Literal['DEBUG', 'INFO', 'ERROR', 'WARNING'] = 'DEBUG'):
    while len(logging.root.handlers) > 0:
        logging.root.removeHandler(logging.root.handlers[-1])

    logging.basicConfig(
        level=getattr(logging, level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        force=True
    )


async def calculate_distance(point, user_coordinates):
    return distance(user_coordinates, (point["coordinates"]["lat"], point["coordinates"]["lon"])).km


async def find_matching_points(points, lat, lon):
    tasks = []
    for point in points:
        task = asyncio.create_task(calculate_distance(point, (lat, lon)))
        tasks.append(task)
    distances = await asyncio.gather(*tasks)
    return [(point, distance) for point, distance in zip(points, distances)]


async def find_closest(points, lat, lon):
    output = []
    matching_points = await find_matching_points(points, lat, lon)
    closest_point = min(matching_points, key=lambda x: x[1])[0]
    text = await get_point_text(closest_point)
    return text


def to_camel(string: str) -> str:
    """
    Верблюдезирует строку, со строчным написанием первого слова

    to_camel_case -> toCamelCase

    :param string: строка в snake case'е
    :type string: str
    :return: строка в camel case'е
    :rtype: str
    """
    return ''.join(word if i == 0 else word.capitalize() for i, word in enumerate(string.split('_')))


def to_snake(string: str) -> str:
    """
    Из CamelCase в snake_case
    """
    return re.sub('(?!^)([A-Z]+)', r'_\1', string).lower()


def to_cebab(string: str) -> str:
    """
    Из CamelCase в cebab-case
    """
    return re.sub('(?!^)([A-Z]+)', r'-\1', string).lower()
