from dataclasses import dataclass
from typing import Dict, List, Any, Callable
import random

@dataclass
class Task:
    id: str
    title: str
    description: str
    examples: List[Dict[str, Any]]  # список примеров входных и выходных данных
    test_cases: List[Dict[str, Any]]  # тестовые случаи для проверки
    points: int  # очки за решение

# Функции для генерации тестовых случаев
def generate_sum_array_tests(count: int) -> List[Dict[str, Any]]:
    tests = []
    for _ in range(count):
        arr = [random.randint(-100, 100) for _ in range(random.randint(3, 10))]
        tests.append({"input": arr, "output": sum(arr)})
    return tests

def generate_find_max_tests(count: int) -> List[Dict[str, Any]]:
    tests = []
    for _ in range(count):
        arr = [random.randint(-100, 100) for _ in range(random.randint(3, 10))]
        tests.append({"input": arr, "output": max(arr)})
    return tests

def generate_is_prime_tests(count: int) -> List[Dict[str, Any]]:
    def is_prime(n: int) -> bool:
        if n < 2:
            return False
        for i in range(2, int(n ** 0.5) + 1):
            if n % i == 0:
                return False
        return True
    
    tests = []
    for _ in range(count):
        num = random.randint(1, 100)
        tests.append({"input": num, "output": is_prime(num)})
    return tests

# Список доступных задач
TASKS: Dict[str, Task] = {
    "sum_array": Task(
        id="sum_array",
        title="Сумма элементов массива",
        description="""
Напишите функцию sum_array(arr), которая принимает список чисел и возвращает их сумму.

Формат ввода:
- arr: список целых чисел

Формат вывода:
- целое число - сумма всех элементов массива

Ограничения:
- Длина массива от 1 до 100
- Элементы массива от -1000 до 1000
""",
        examples=[
            {"input": [1, 2, 3], "output": 6},
            {"input": [-1, 0, 1], "output": 0},
        ],
        test_cases=generate_sum_array_tests(5),
        points=10
    ),
    
    "find_max": Task(
        id="find_max",
        title="Поиск максимального элемента",
        description="""
Напишите функцию find_max(arr), которая находит максимальный элемент в списке.

Формат ввода:
- arr: список целых чисел

Формат вывода:
- целое число - максимальный элемент массива

Ограничения:
- Длина массива от 1 до 100
- Элементы массива от -1000 до 1000
""",
        examples=[
            {"input": [1, 3, 2], "output": 3},
            {"input": [-1, -5, -2], "output": -1},
        ],
        test_cases=generate_find_max_tests(5),
        points=10
    ),
    
    "is_prime": Task(
        id="is_prime",
        title="Проверка числа на простоту",
        description="""
Напишите функцию is_prime(n), которая проверяет, является ли число простым.

Формат ввода:
- n: целое положительное число

Формат вывода:
- bool: True если число простое, False иначе

Ограничения:
- 1 ≤ n ≤ 1000
""",
        examples=[
            {"input": 7, "output": True},
            {"input": 4, "output": False},
        ],
        test_cases=generate_is_prime_tests(5),
        points=15
    )
} 