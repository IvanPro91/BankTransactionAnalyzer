from src.utils import (
    currency_rates,
    get_period_date,
    main_cards,
    read_finance_excel_operation,
    top_transactions,
    user_stocks,
    welcome_text,
)


def page_main(date: str) -> dict:
    """
    Функция главной страницы возвращает основную информацию.
    :param date: Входящая дата.
    :return: Json объект содержащий информацию.
    """
    period_date = get_period_date(date)
    struct_file_json = read_finance_excel_operation(period_date)
    json_response = {
        "greeting": welcome_text(date),
        "cards": main_cards(struct_file_json),
        "top_transactions": top_transactions(struct_file_json),
        "currency_rates": currency_rates(),
        "stock_prices": user_stocks(),
    }
    return json_response
