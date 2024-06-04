import asyncio
import json

import aiohttp


async def func():
    async with aiohttp.ClientSession() as session:
        url = 'https://api.eco.blcp.ru/api/router/getcount?territory=&type_of_institution=&unit_type=0'
        async with session.get(url) as response:
            p = await response.text()
            data = json.loads(p)
    return data


async def text_top_schools(count=10, count_detail=0,
                     display_options=['Макулатура', 'Пластик', 'Крышки', 'Стекло', 'Металл', 'Батарейки']):
    text = ''
    unit = "кг"
    schools = await func()
    schools = schools[:count]
    count = len(schools)
    for i in range(count):
        text += f'<b>{i + 1}) {schools[i]["school"]}</b>\n'
        if i < count_detail:
            mass_grops = 0
            count_grops = 0
            for material in display_options:
                if not schools[i]["groups"].get(material, False):
                    continue
                mass_grops += schools[i]["groups"][material]
                count_grops += 1
                text += f'\t{material}: {round(schools[i]["groups"][material], 2)} {unit}\n'

            if len(schools[i]["groups"].keys()) != count_grops + 1 and mass_grops < schools[i]["groups"]["Итого"]:
                text += f'\tПрочее: {round(schools[i]["groups"]["Итого"] - mass_grops, 2)} {unit}\n'

        text += f'\tВсего сдано: {round(schools[i]["groups"]["Итого"], 2)} {unit}\n\n'

    return text


