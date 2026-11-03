def calculate_price_trend(history_data, forecast_steps=3):
    if not history_data or len(history_data) < 2:
        return {
            "trend": "Nincs elég adat",
            "slope": 0,
            "percent_change": 0,
            "current_price": history_data[0]["price"] if history_data else 0,
            "forecast_price": history_data[0]["price"] if history_data else 0,
            "recommendation": "Legalább 2 különböző időpontból származó áradat szükséges az elemzéshez.",
            "badge_class": "secondary",
            "trendline_points": [],
            "forecast_points": []
        }

    prices = [entry["price"] if isinstance(entry, dict) else entry[1] for entry in history_data]
    n = len(prices)
    x = list(range(n))
    y = prices

    mean_x = sum(x) / n
    mean_y = sum(y) / n

    numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
    denominator = sum((x[i] - mean_x) ** 2 for i in range(n))

    if denominator == 0:
        slope = 0.0
    else:
        slope = numerator / denominator

    intercept = mean_y - slope * mean_x

    trendline_points = [round(slope * i + intercept) for i in range(n)]

    future_x = (n - 1) + forecast_steps
    forecast_price = round(slope * future_x + intercept)
    forecast_price = max(0, forecast_price)

    current_price = prices[-1]
    if current_price > 0:
        percent_change = ((forecast_price - current_price) / current_price) * 100
    else:
        percent_change = 0.0

    if percent_change <= -2.0:
        trend = "Csökkenő"
        recommendation = "Az árak csökkenő pályán mozognak. Érdemes várni a vásárlással, további áresés valószínű."
        badge_class = "success"
    elif percent_change >= 2.0:
        trend = "Emelkedő"
        recommendation = "Dráguló tendencia érzékelhető! Ha szükséged van a termékre, érdemes mihamarabb beszerezni."
        badge_class = "danger"
    else:
        trend = "Stagnáló"
        recommendation = "Kiegyensúlyozott piaci ár. Jelentős elmozdulás rövid távon nem várható."
        badge_class = "secondary"

    forecast_points = []
    for step in range(1, forecast_steps + 1):
        pred = round(slope * ((n - 1) + step) + intercept)
        forecast_points.append(max(0, pred))

    return {
        "trend": trend,
        "slope": round(slope, 2),
        "percent_change": round(percent_change, 1),
        "current_price": current_price,
        "forecast_price": forecast_price,
        "recommendation": recommendation,
        "badge_class": badge_class,
        "trendline_points": trendline_points,
        "forecast_points": forecast_points
    }