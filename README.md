### Быстрый старт

1. Устанавливаем python 3.10
2. Создаём виртуальное окружение для проекта (через IDE или через `python -m venv ./venv` в корне проекта)
3. Активируем окружение в консоли (выполняем `./venv/bin/activate` или `activate.ps1` для windows)
4. Устанавливаем зависимости через `python -m pip install -r ./requirements.txt`
5. Создаём файл .env (в корневой папке проекта) по образцу из .env.example (это только пример заполнения, полный список
   переменных можно найти в `bot/core/config::Config`)
6. Добавляем директорию `/bot` в `PYTHONPATH` переменную среды (чтобы все импорты не содержали `bot.`)
    - при запуске через консоль ничего делать не нужно `python bot/main.py` уже будет работать
    - при запуске через pycharm необходимо ткнуть на директорию _bot_ в файлах проекта, а
      затем `Mark directory as`->`Sources root`
    - при запуске через VS code нужно добавить папку `bot` в переменную среды `PYTHONPATH` через
      магию https://copyprogramming.com/howto/how-to-setup-pythonpath-env-in-vscode-properly
7. Поднимаем базу данных (`docker-compose up -d database`)
8. создаём alembic.ini по образу из alembic.ini.example и заполняем в нём `sqlalchemy.url` данными для подключения к БД
9. накатываем миграции командой ` python -m alembic upgrade head`
10. Запускаем `bot/main.py`

### Другой способ

1. Создаём файл .env (в корневой папке проекта) по образцу из .env.example (это только пример заполнения, полный список
   переменных можно найти в `bot/core/config::Config`)
2. Откройте терминал и перейдите в директорию с вашим проектом.
3. Выполните команду для сборки Docker образа: `docker build -t mytelegrambot .`
4. Выполните команду для запуска Docker контейнеров: `docker-compose up`

