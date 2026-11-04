import pytest
from analytics import calculate_price_trend


def test_insufficient_data_empty():
    
    result = calculate_price_trend([])
    assert result["trend"] == "Nincs elég adat"
    assert result["slope"] == 0
    assert result["percent_change"] == 0
    assert result["current_price"] == 0
    assert result["forecast_price"] == 0
    assert result["badge_class"] == "secondary"
    assert result["trendline_points"] == []
    assert result["forecast_points"] == []


def test_insufficient_data_single_item():
    
    data = [{"checked_at": "2026-10-28 00:00:00", "price": 150000}]
    result = calculate_price_trend(data)
    assert result["trend"] == "Nincs elég adat"
    assert result["slope"] == 0
    assert result["percent_change"] == 0
    assert result["current_price"] == 150000
    assert result["forecast_price"] == 150000
    assert result["trendline_points"] == []
    assert result["forecast_points"] == []


def test_rising_trend_detection():
    
    data = [
        {"checked_at": "2026-10-28 00:00:00", "price": 180000},
        {"checked_at": "2026-10-29 00:00:00", "price": 185000},
        {"checked_at": "2026-11-01 00:00:00", "price": 190000},
        {"checked_at": "2026-11-03 00:00:00", "price": 198000},
    ]
    result = calculate_price_trend(data, forecast_steps=3)

    assert result["trend"] == "Emelkedő"
    assert result["badge_class"] == "danger"
    assert result["slope"] > 0
    assert result["percent_change"] >= 2.0
    assert result["current_price"] == 198000
    assert result["forecast_price"] > result["current_price"]
    assert len(result["trendline_points"]) == 4
    assert len(result["forecast_points"]) == 3


def test_falling_trend_detection():
    
    data = [
        {"checked_at": "2026-10-28 00:00:00", "price": 250000},
        {"checked_at": "2026-10-29 00:00:00", "price": 242000},
        {"checked_at": "2026-11-01 00:00:00", "price": 235000},
        {"checked_at": "2026-11-03 00:00:00", "price": 228000},
    ]
    result = calculate_price_trend(data, forecast_steps=3)

    assert result["trend"] == "Csökkenő"
    assert result["badge_class"] == "success"
    assert result["slope"] < 0
    assert result["percent_change"] <= -2.0
    assert result["current_price"] == 228000
    assert result["forecast_price"] < result["current_price"]
    assert len(result["trendline_points"]) == 4
    assert len(result["forecast_points"]) == 3


def test_stagnating_trend_detection():
    
    data = [
        {"checked_at": "2026-10-28 00:00:00", "price": 253000},
        {"checked_at": "2026-10-29 00:00:00", "price": 252800},
        {"checked_at": "2026-11-01 00:00:00", "price": 253100},
        {"checked_at": "2026-11-03 00:00:00", "price": 252790},
    ]
    result = calculate_price_trend(data, forecast_steps=3)

    assert result["trend"] == "Stagnáló"
    assert result["badge_class"] == "secondary"
    assert -2.0 < result["percent_change"] < 2.0
    assert result["current_price"] == 252790


def test_tuple_input_compatibility():
    
    data = [
        ("2026-10-28 00:00:00", 100000),
        ("2026-10-29 00:00:00", 110000),
        ("2026-10-30 00:00:00", 120000),
    ]
    result = calculate_price_trend(data, forecast_steps=2)

    assert result["trend"] == "Emelkedő"
    assert result["current_price"] == 120000
    assert len(result["forecast_points"]) == 2


def test_forecast_price_non_negative():
    
    data = [
        {"checked_at": "2026-10-28 00:00:00", "price": 10000},
        {"checked_at": "2026-10-29 00:00:00", "price": 1000},
    ]
    result = calculate_price_trend(data, forecast_steps=5)

    assert result["trend"] == "Csökkenő"
    assert result["forecast_price"] >= 0
    for pt in result["forecast_points"]:
        assert pt >= 0