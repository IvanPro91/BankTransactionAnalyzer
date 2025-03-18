from typing import Any
from unittest.mock import patch

from src.views import page_main


@patch("requests.get")
@patch("src.utils.user_stocks")
@patch("src.utils.currency_rates")
def test_page_main(user_stocks: Any, currency_rates: Any, requests_mock: Any) -> None:
    """
    Тестирование основной функции
    """
    requests_mock.return_value.json.return_value = {}
    user_stocks.return_value = {}
    currency_rates.return_value = {}
    data = page_main("2021-12-27 08:00:23")
    assert data == {
        "cards": [
            {"cashback": 41.0, "last_digits": "4556", "total_spent": 24452.9},
            {"cashback": 0.0, "last_digits": "5091", "total_spent": 16360.710000000001},
            {"cashback": 0.0, "last_digits": "7197", "total_spent": 20935.68},
        ],
        "currency_rates": [{"currency": "USD", "rate": 0}, {"currency": "EUR", "rate": 0}],
        "greeting": "Доброе утро",
        "stock_prices": [
            {"price": 0, "stock": "AAPL"},
            {"price": 0, "stock": "AMZN"},
            {"price": 0, "stock": "GOOGL"},
            {"price": 0, "stock": "MSFT"},
            {"price": 0, "stock": "TSLA"},
        ],
        "top_transactions": [
            {
                "amount": 28001.94,
                "category": "Переводы",
                "date": "23.12.2021",
                "description": "Перевод Кредитная карта. ТП 10.2 RUR",
            },
            {
                "amount": 28001.94,
                "category": "Переводы",
                "date": "23.12.2021",
                "description": "Перевод Кредитная карта. ТП 10.2 RUR",
            },
            {"amount": 20000.0, "category": "Другое", "date": "23.12.2021", "description": "Иван С."},
            {"amount": 14216.42, "category": "ЖКХ", "date": "16.12.2021", "description": "ЖКУ Квартира"},
            {"amount": 10000.0, "category": "Переводы", "date": "23.12.2021", "description": "Светлана Т."},
        ],
    }
