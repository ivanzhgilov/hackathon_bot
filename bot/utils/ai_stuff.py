import csv
from asyncio import set_event_loop_policy, WindowsSelectorEventLoopPolicy, run

import aiofiles
import g4f.models as models
from g4f.client import Client

# Set the event loop policy for Windows
set_event_loop_policy(WindowsSelectorEventLoopPolicy())


async def get_categories() -> list:
    categories = []
    async with aiofiles.open('БЗ.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(await csvfile.read(), delimiter=';')
        for row in reader:
            if row:
                categories.append(row[0])
    return categories


async def get_instruction(category) -> str:
    instruction = None
    async with aiofiles.open('БЗ.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(await csvfile.read(), delimiter=';')
        for row in reader:
            if len(row) > 1:
                if row[0] == category:
                    instruction = row[1]
                    break
    return instruction


async def ask_gpt(question) -> str:
    client = Client()
    response = client.chat.completions.create(
        model=models.gpt_4,
        messages=[{"role": "user", "content": question}]
    )
    return response.choices[0].message.content


async def get_ai_answer(question) -> str:
    question_about_category = (f'На основе категорий вопросов, скажи к какой категории относится вопрос {question}.'
                               f' Пиши в таком формате: name: название категории. Вот Категории вопросов:'
                               f' {", ".join(await get_categories())} Если ни одна категория не подходит пиши: name: ошибка')
    category = (await ask_gpt(question_about_category)).split(': ')[1]
    if 'ошибка' in category:
        return 'Нейросеть не смогла ответить на ваш вопрос'
    else:
        instruction = await get_instruction(category)
        if instruction:
            question_about_instruction = (f'используя данную инструкцию, напиши ответ на вопрос {question}. Если этой'
                                          f' инструкции недостаточно для ответа на вопрос, пиши'
                                          f' "Нейросеть не смогла ответить на ваш вопрос". Вот инсрукция {instruction}')
            return await ask_gpt(question_about_instruction)
        else:
            return 'Инструкция не найдена'

