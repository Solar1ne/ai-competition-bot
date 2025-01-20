from config import GIGAKEY
from langchain_gigachat.chat_models import GigaChat
from langchain_core.messages import HumanMessage, SystemMessage

LLM = GigaChat(
    credentials=GIGAKEY,
    scope="GIGACHAT_API_PERS",
    model="GigaChat",
    verify_ssl_certs=False,
    streaming=False,
)

def get_hint(user_message: str) -> str:
    """
    Функция отправляет текст задания в модель GigaChat и возвращает подсказку.

    :param user_message: текст задания
    :return: текст подсказки
    """
    messages = [
        SystemMessage(
            content=(
                "Ты - эксперт по спортивному программированию на Python. "
                "Твоя задача - помогать пользователям с решением задач, но не давать готовый ответ, "
                "а лишь подсказки к решению трех заданий:"
                "задание 1: Напишите функцию sum_array(arr), которая принимает список чисел и возвращает их сумму. Формат ввода: - arr: список целых чисел.  Формат вывода: - целое число - сумма всех элементов массива. Ограничения: - Длина массива от 1 до 100 - Элементы массива от -1000 до 1000"
                "задание 2: Напишите функцию find_max(arr), которая находит максимальный элемент в списке. Формат ввода: - arr: список целых чисел"
                "задание 3: Напишите функцию is_prime(n), которая проверяет, является ли число простым. Формат ввода:- n: целое положительное число Формат вывода: - bool: True если число простое, False иначе. Формат вывода:- bool: True если число простое, False иначе."
            )
        ),
        HumanMessage(content=user_message),
    ]

    response = LLM.invoke(messages)
    return response.content
