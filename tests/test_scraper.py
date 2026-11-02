import pytest
from scraper import (
    parse_price,
    detect_category,
    normalize_shop_name,
    parse_arukereso_html
)

SAMPLE_HTML = """
<html>
    <body>
        <h1>AMD Ryzen 7 7800X3D Processzor</h1>
        <div class="optoffer">
            <span class="shop-name">Ismeretlen Kis Bolt Kft.</span>
            <span class="price">140 000 Ft</span>
        </div>
        <div class="optoffer">
            <span class="shop-name">Alza.hu</span>
            <span class="price">168 900 Ft</span>
        </div>
        <div class="optoffer">
            <span class="shop-name">iPon Computer</span>
            <span class="price">164 500 Ft</span>
        </div>
        <div class="optoffer">
            <span class="shop-name">Foramax</span>
            <span class="price">162 900 Ft</span>
        </div>
        <div class="optoffer">
            <span class="shop-name">Computer Imperium</span>
            <span class="price">165 000 Ft</span>
        </div>
    </body>
</html>
"""

def test_parse_price():
    assert parse_price("244 500 Ft") == 244500
    assert parse_price("52.990 Ft-tól") == 52990

def test_detect_hardware_categories():
    assert detect_category("Kingston FURY Beast 32GB DDR5 6000MHz") == "RAM"
    assert detect_category("AMD Ryzen 7 7800X3D Processzor") == "CPU"
    assert detect_category("ASUS GeForce RTX 4070 Super") == "GPU"

def test_normalize_all_ten_target_shops():
    assert normalize_shop_name("PCX.hu logó") == "PCX"
    assert normalize_shop_name("iPon") == "iPon"
    assert normalize_shop_name("Media Markt") == "MediaMarkt"
    assert normalize_shop_name("Alza.hu") == "Alza"
    assert normalize_shop_name("AQUA Webáruház") == "Aqua"
    assert normalize_shop_name("Konzolvilág") == "Konzolvilág"
    assert normalize_shop_name("Skynet Computer") == "Skynet"
    assert normalize_shop_name("Komphone") == "Komphone"
    assert normalize_shop_name("Foramax") == "Foramax"
    assert normalize_shop_name("Computer Imperium") == "Computer Imperium"
    assert normalize_shop_name("Valami Más Bolt") is None

def test_filters_out_unknown_shops_and_finds_cheapest():
    result = parse_arukereso_html(SAMPLE_HTML)

    assert result["name"] == "AMD Ryzen 7 7800X3D Processzor"
    assert result["category"] == "CPU"
    assert len(result["offers"]) == 4
    assert result["best_shop"] == "Foramax"
    assert result["best_price"] == 162900

def test_arukereso_no_offers_raises_error():
    empty_html = "<html><body><h1>AMD Ryzen 5 7600X</h1></body></html>"
    with pytest.raises(ValueError):
        parse_arukereso_html(empty_html)