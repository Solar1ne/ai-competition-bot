import os

BOT_TOKEN = "8051595922:AAHwRwje4s1Q5nqKnq0Tg2Cpik4cx96m22c"
GIGAKEY = "MWE4OTYzZDctZDIzNS00ZjZmLTljMjMtNzg1NmZmZGI1OWE3OjZjODAyZmUwLWEwZmQtNGRiMS1iNGJhLWI3Y2VlZTBiMmU2Mg=="
DATA_FILE = "data/users.csv"
LEADERBOARD_FILE = "data/leaderboard.csv"

# Создаем пустые файлы если их нет
for file in [DATA_FILE, LEADERBOARD_FILE]:
    if not os.path.exists(file):
        os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, 'w') as f:
            if file == LEADERBOARD_FILE:
                f.write("name,score\n")  # Заголовок для таблицы лидеров