import os.path
from dataclasses import dataclass

from pandas import DataFrame
from requests import Response

from config import ROOT_DIR, API_KEY_STOCKS, API_KEY, FILE_EXCEL, USER_SETTINGS
from settings_logger import module_logger
from datetime import datetime
from logging import Logger
import pandas as pd
import requests
import json

logger: Logger = module_logger(__name__)


class FileNotExistsError(Exception):
    pass


def get_period_date(date: str) -> tuple[datetime, datetime]:
    """
    Функция получения периода дат с начала месяца до указанной даты
    :param date: Строка даты
    :return: Тип datetime
    """
    format_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    start_day = format_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_day = format_date.replace(hour=0, minute=0, second=0, microsecond=0)
    logger.info("Кортеж с периодам дат создан успешно")
    return start_day, end_day


def read_finance_excel_operation(period_datetime: tuple, filename: str | None = FILE_EXCEL) -> DataFrame:
    """
    Функция для считывания финансовых операций из Excel выдает список словарей с транзакциями.
    :param filename: Путь к файлу Excel.
    :param period_datetime: Лист с периодом начала мес и указанной датой для сортировки
    :return: Список словарей с транзакциями.
    """
    chk_path = os.path.exists(filename)
    if chk_path:
        try:
            excel_data: DataFrame = pd.read_excel(filename)
            start_date, end_date = period_datetime
            excel_data["Дата операции"] = pd.to_datetime(excel_data["Дата операции"], dayfirst=True)
            df: DataFrame = excel_data[
                (excel_data["Дата операции"] >= start_date) & (excel_data["Дата операции"] <= end_date)
            ]
            logger.info("Данные по файлу транзакций отфильтрован по дате и готов к работе")
            return df
        except Exception:
            logger.error("Произошла ошибка в чтении файла и/или в преобразовании ячейки в формат даты")
            raise Exception("Произошла ошибка в чтении файла и/или в преобразовании ячейки в формат даты")
    else:
        logger.error("filename не указан и равен None")
        raise FileNotExistsError("Файл не существует!")


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
    logger.info("Успешно определено время, приветствие сформировано")
    return welcome


def main_cards(transactions: DataFrame) -> list[dict]:
    """
    Функция вывода всей информации по картам.
    :param transactions: Входные данные с транзакциями.
    :return: Информация по картам.
    """
    try:
        add_group_data: DataFrame = transactions.groupby("Номер карты").agg({"Сумма операции с округлением": "sum"})
        info_card: list = [
            {
                "last_digits": str(card_num)[-4:],
                "total_spent": float(row["Сумма операции с округлением"]),
                "cashback": round(float(row["Сумма операции с округлением"]) / 100, 2),
            }
            for card_num, row in add_group_data.iterrows()
        ]
        logger.info("Список карт успешно сформирован в лист")
        return info_card
    except Exception:
        logger.error("Empty DataFrame - данные пусты, поменяйте дату")
        raise ValueError("Empty DataFrame - данные пусты, поменяйте дату")


def top_transactions(transactions: DataFrame) -> list[dict]:
    """
    Функция возврата ТОП 5 транзакций.
    :param transactions: Список транзакций.
    :return: Список ТОП 5 транзакций по сумме.
    """
    top_data: DataFrame = transactions.sort_values(by="Сумма операции с округлением", ascending=False).head()
    top_transaction: list[dict] = [
        {
            "date": row["Дата платежа"],
            "amount": float(row["Сумма операции с округлением"]),
            "category": row["Категория"],
            "description": row["Описание"],
        }
        for data, row in top_data.iterrows()
    ]
    logger.info("Список ТОП 5 транзакций сформирован")
    return top_transaction


def get_api_currency(currency: str) -> float:
    """
    Функция получения курса валюты по API
    :param currency: Название валюты
    :return: Результат курса валюты
    """
    date: str = datetime.now().strftime("%Y-%m-%d")
    url: str = f"https://api.apilayer.com/exchangerates_data/{date}"
    params: dict = {"base": currency, "symbols": "RUB"}
    headers: dict = {"apikey": API_KEY}
    try:
        response: Response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            rates = data["rates"]["RUB"]
            logger.info("Данные API успешно запрошены")
            return float(rates)
    except Exception as err:
        logger.error(err)
        raise err
    logger.warning("Возвращаем '0' что-то с запросом API пошло не так")
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
        response: Response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            logger.info("Данные API успешно запрошены")
            return float(data["Global Quote"]["05. price"])
    except Exception as err:
        logger.error(err)
    logger.warning("Возвращаем '0' что-то с запросом API пошло не так")
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
    logger.info("Курс валют успешно возвращен")
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
    logger.info("Стоимости акций успешно возвращены")
    return data_stocks


def get_user_settings() -> dict:
    """
    Функция чтения пользовательских настроек.
    :return: Json объект Python.
    """
    try:
        with open(USER_SETTINGS, encoding="utf-8") as f:
            data = dict(json.load(f))
            logger.info("Файл настроек успешно считан")
        return data
    except Exception as err:
        logger.error(err)
        raise err


def notifications(date: str, params_date: str | None = None) -> datetime:
    """
    W — неделя, на которую приходится дата;
    M — месяц, на который приходится дата;
    Y — год, на который приходится дата;
    ALL — все данные до указанной даты.
    """
    datetime_ = datetime.strptime(date, "%Y-%m-%d")
    match params_date:
        case "W":
            day_index = datetime_.weekday()
            return datetime_.replace(day=datetime_.day - day_index)
        case "M":
            return datetime_.replace(day=1)
        case "Y":
            return datetime_.replace(month=1)
        case "ALL":
            return datetime_.replace(year=1980)
        case _:
            return datetime_.replace(day=1)


def expenses_total_amount(df: DataFrame):
    filter_df = df[df["Сумма платежа"] < 0]
    agg_df = filter_df.agg({"Сумма платежа": "sum"})
    float_result = agg_df.abs()["Сумма платежа"]
    return round(float(float_result), 2)


def income_total_amount(df: DataFrame):
    filter_df = df[df["Сумма платежа"] > 0]
    float_result = filter_df.agg({"Сумма платежа": "sum"})["Сумма платежа"]
    return round(float(float_result), 2)
