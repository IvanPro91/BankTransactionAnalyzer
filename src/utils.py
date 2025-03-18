import json
import os
from datetime import datetime
from typing import Any

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API_KEY = os.getenv("API_KEY")
API_KEY_STOCKS = os.getenv("API_KEY_STOCKS")


def read_finance_excel_operation(filename: str | None = ROOT_DIR + "/data/operations.xlsx") -> list[dict[Any, Any]]:
    """
    Функция для считывания финансовых операций из Excel выдает список словарей с транзакциями.
    :param filename: Путь к файлу Excel.
    :return: Список словарей с транзакциями.
    """
    if filename:
        excel_data = pd.read_excel(filename)
        group_data = excel_data.to_dict("records")
        return list(group_data)
    else:
        raise ValueError("filename не указан и равен None")


def welcome_text(date: str) -> str:
    """
    Функция возврата строки приветствия по дате форматом YYYY-MM-DD HH:MM:SS.
    :param date: Дата формата YYYY-MM-DD HH:MM:SS.
    :return: Приветствие от переданного времени.
    """
    input_datetime = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    hour = input_datetime.hour
    if 4 <= hour <= 11:
        welcome = "Доброе утро"
    elif 12 <= hour < 17:
        welcome = "Добрый день"
    elif 17 <= hour < 22:
        welcome = "Добрый вечер"
    else:
        welcome = "Доброй ночи"
    return welcome


def main_cards(transactions: list[dict]) -> list[dict]:
    """
    Функция вывода всей информации по картам.
    :param transactions: Входные данные с транзакциями.
    :return: Информация по картам.
    """
    df = pd.DataFrame(transactions)
    cards = []
    add_group_data = df.groupby("Номер карты").agg({"Сумма операции с округлением": "sum", "Кэшбэк": "sum"})
    for card_num, row in add_group_data.iterrows():
        info_card = {
            "last_digits": str(card_num)[-4:],
            "total_spent": float(row["Сумма операции с округлением"]),
            "cashback": float(row["Кэшбэк"]),
        }
        cards.append(info_card)
    return cards


def top_transactions(transactions: list[dict]) -> list[dict]:
    """
    Функция возврата ТОП 5 транзакций.
    :param transactions: Список транзакций.
    :return: Список ТОП 5 транзакций по сумме.
    """
    top_transaction = []
    df = pd.DataFrame(transactions)
    top_data = df.sort_values(by="Сумма операции с округлением", ascending=False).head(5)
    for data, row in top_data.iterrows():
        top_transaction.append(
            {
                "date": row["Дата платежа"],
                "amount": float(row["Сумма операции с округлением"]),
                "category": row["Категория"],
                "description": row["Описание"],
            }
        )
    return top_transaction


def get_api_currency(currency: str) -> float:
    """
    Функция получения курса валюты по API
    :param currency: Название валюты
    :return: Результат курса валюты
    """
    date = datetime.now().strftime("%Y-%m-%d")
    url = f"https://api.apilayer.com/exchangerates_data/{date}"
    params = {"base": currency, "symbols": "RUB"}
    headers = {"apikey": API_KEY}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=3)
        if response.status_code == 200:
            data = response.json()
            rates = data["rates"]["RUB"]
            return float(rates)
    except requests.exceptions.ReadTimeout:
        raise requests.exceptions.ReadTimeout("Превышено время соединения с сервером API")
    return 0


def get_api_stocks(stocks: str) -> float:
    """
    Функция получения стоимости акций.
    :param stocks: Название акции.
    :return: Стоимость.
    """
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": stocks,
        "apikey": API_KEY_STOCKS,
    }
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return float(data["Global Quote"]["05. price"])
    except Exception:
        raise Exception("Произошла ошибка")
    return 0


def currency_rates() -> list[dict]:
    """
    Функция возвращает курс валют.
    :return: Курсы валют.
    """
    user_settings = get_user_settings()
    user_currencies = user_settings["user_currencies"]
    data_rates = []
    for currency in user_currencies:
        rates = get_api_currency(currency)
        data_rates.append({"currency": currency, "rate": round(rates, 2)})
    return data_rates


def user_stocks() -> list[dict]:
    """
    Функция возвращает стоимость акций.
    :return: Список стоимости акций.
    """
    user_settings = get_user_settings()
    all_stocks = user_settings["user_stocks"]
    data_stocks = []
    for stocks in all_stocks:
        stock = get_api_stocks(stocks)
        data_stocks.append({"stock": stocks, "price": round(stock, 2)})
    return data_stocks


def get_user_settings() -> dict:
    """
    Функция чтения пользовательских настроек.
    :return: Json объект Python.
    """
    try:
        with open(ROOT_DIR + "/user_settings.json") as f:
            return dict(json.load(f))
    except FileNotFoundError:
        raise FileNotFoundError("Ошибка открытия файла, файл не существует")
    except Exception:
        raise Exception("Ошибка чтения структуры json файла")
