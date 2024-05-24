import asyncio
import logging
import re
from typing import Literal

import argon2
from geopy.adapters import AioHTTPAdapter
from geopy.distance import distance
from geopy.geocoders import Nominatim


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
    matching_points = await find_matching_points(points, user_waste_categories, lat, lon)
    if matching_points:
        closest_point = min(matching_points, key=lambda x: x[1])[0]
        text = f"""{closest_point['title']}
        
{closest_point['description']}

{closest_point['address']}

Принимается: {', '.join(closest_point['types_of_garbage'])}

Номер телефона: {closest_point['phone_number']}"""
        return text
    else:
        tasks = [asyncio.create_task(calculate_distance(point, (lat, lon))) for point in points if
                 set(user_waste_categories).issubset(set(point["types_of_garbage"]))]
        distances = await asyncio.gather(*tasks)
        sorted_points = sorted([(point, distance) for point, distance in zip(points, distances)], key=lambda x: x[1])
        lst = []
        print(
            "There is no point where you can dispose of all your waste. Here are the nearest points for each type of waste:")
        for point, distance in sorted_points:
            text = f"""{point['title']}
            
            {point['description']}
            
            {point['address']}
            
            Принимается: {', '.join(point['types_of_garbage'])}
            
            Номер телефона: {point['phone_number']}"""
            lst.append(text)
        return "\n".join(lst)


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
