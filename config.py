import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Получаем значения из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
GIGAKEY = os.getenv("GIGAKEY")

if not BOT_TOKEN or not GIGAKEY:
    raise ValueError("Необходимо указать BOT_TOKEN и GIGAKEY в файле .env")

# Создаем пустые файлы если их нет
DATA_FILE = "data/users.csv"
LEADERBOARD_FILE = "data/leaderboard.csv"

for file in [DATA_FILE, LEADERBOARD_FILE]:
    if not os.path.exists(file):
        os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, 'w') as f:
            if file == LEADERBOARD_FILE:
                f.write("name,score\n")  # Заголовок для таблицы лидеров