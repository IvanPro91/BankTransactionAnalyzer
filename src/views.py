from datetime import datetime

from pandas import DataFrame

from src.utils import (
    currency_rates,
    get_period_date,
    main_cards,
    read_finance_excel_operation,
    top_transactions,
    user_stocks,
    welcome_text,
    notifications,
    expenses_total_amount,
    income_total_amount,
)


def page_main(date: str) -> dict:
    """
    Функция главной страницы возвращает основную информацию.
    :param date: Входящая дата.
    :return: Json объект содержащий информацию.
    """
    period_date: tuple[datetime, datetime] = get_period_date(date)
    struct_file_json: DataFrame = read_finance_excel_operation(period_date)

    data = {
        "greeting": welcome_text(date),
        "cards": main_cards(struct_file_json),
        "top_transactions": top_transactions(struct_file_json),
        "currency_rates": currency_rates(),
        "stock_prices": user_stocks(),
    }
    return data


def page_notification(date: str):
    end_day: datetime = datetime.strptime(date, "%Y-%m-%d")
    start_day: datetime = notifications(date, "W")
    period_date: tuple[datetime, datetime] = (start_day, end_day)
    struct_file_json: DataFrame = read_finance_excel_operation(period_date)
    print(expenses_total_amount(struct_file_json))
    data = {
        "expenses": {
            "total_amount": expenses_total_amount(struct_file_json),
            "main": [{"category": "Супермаркеты", "amount": 17319}],
            "transfers_and_cash": [{"category": "Наличные", "amount": 500}],
        },
        "income": {
            "total_amount": income_total_amount(struct_file_json),
            "main": [{"category": "Пополнение_BANK007", "amount": 33000}],
        },
        "currency_rates": currency_rates(),
        "stock_prices": user_stocks(),
    }
    return data
