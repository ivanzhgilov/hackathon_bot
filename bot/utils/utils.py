import asyncio
import logging
import re
from typing import Literal

import aiohttp
import argon2
from geopy.adapters import AioHTTPAdapter
from geopy.distance import distance
from geopy.geocoders import Nominatim


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


async def find_matching_points(points, user_waste_categories, lat, lon):
    tasks = [asyncio.create_task(calculate_distance(point, (lat, lon)))
             for point in points if
             set(user_waste_categories).issubset(set(point["types_of_garbage"]))]
    distances = await asyncio.gather(*tasks)
    return [(point, distance) for point, distance in zip(points, distances) if
            set(user_waste_categories).issubset(set(point["types_of_garbage"]))]


async def find_closest(points, user_waste_categories, lat, lon):
    output = []
    matching_points = await find_matching_points(points, user_waste_categories, lat, lon)
    if matching_points:
        closest_point = min(matching_points, key=lambda x: x[1])[0]
        text = f"""{closest_point['title']}
        
{closest_point['description']}

{closest_point['address']}

Принимается: {', '.join(closest_point['types_of_garbage'])}

Номер телефона: {closest_point['phone_number']}"""
        output.append(text)
        return output
    else:
        lst = []
        output.append(
            """К сожалению точки в которой вы можете сдать все выбранные категории мусора не нащлось, поэтому вот юлижайшие точки для каждой категории""")
        tasks = [asyncio.create_task(calculate_distance(point, (lat, lon))) for point in points if
                 set(user_waste_categories).issubset(set(point["types_of_garbage"]))]

        for category in user_waste_categories:
            tasks = [asyncio.create_task(calculate_distance(point, (lat, lon))) for point in points if
                     category in point["types_of_garbage"]]
            lst.append(tasks)
        for el in lst:
            distances = await asyncio.gather(*el)
            x = [(point, distance) for point, distance in zip(points, distances)]
            if x:
                closest_point = min(x,
                                    key=lambda x: x[1])[0]
                text = f"""{closest_point['title']}
    
{closest_point['description']}
    
{closest_point['address']}
    
Принимается: {', '.join(closest_point['types_of_garbage'])}
    
Номер телефона: {closest_point['phone_number']}"""
                output.append(text)
        return output


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


print(hash_password("test123"))
