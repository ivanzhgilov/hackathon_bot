import asyncio
import logging
import re
from typing import Literal

from geopy.adapters import AioHTTPAdapter
from geopy.distance import distance
from geopy.geocoders import Nominatim


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
        closest_point = min(matching_points, key=lambda x: x[1])
        return f"The nearest point where you can dispose of all your waste is: {closest_point[0]['title']}"
    else:
        tasks = [asyncio.create_task(calculate_distance(point, (lat, lon))) for point in points if
                 set(user_waste_categories).issubset(set(point["types_of_garbage"]))]
        distances = await asyncio.gather(*tasks)
        sorted_points = sorted([(point, distance) for point, distance in zip(points, distances)], key=lambda x: x[1])
        lst = []
        print(
            "There is no point where you can dispose of all your waste. Here are the nearest points for each type of waste:")
        for point, distance in sorted_points:
            lst.append(f"{point['title']}: {distance:.2f} km away. Accepts: {', '.join(point['types_of_garbage'])}")
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
