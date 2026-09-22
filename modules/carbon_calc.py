"""
Логика расчёта углерода.
Работает с baseline-данными, потому что реальные CCI-растры слишком большие.
Логика полностью соответствует кейсу: E = -ΔC × 44/12.
"""


def simulate_biomass(baseline_row, year_start, year_end, cf):
    """
    Генерирует ряд «условной» биомассы по годам
    на основе скорости изменения запаса из baseline.
    """
    g = float(baseline_row["g_tC_ha_yr"])
    c_start = float(baseline_row["baseline_2019_tC_ha"])

    series = []
    for year in range(year_start, year_end + 1):
        c = max(0.0, c_start + g * (year - year_start))
        series.append({"year": year, "carbon_t_ha": round(c, 3)})

    return series


def compute_carbon(baseline_df, aoi_id, year_start, year_end, cf):
    """Возвращает ряд запаса углерода и его изменение."""
    row = baseline_df[baseline_df["aoi_id"] == aoi_id]
    if row.empty:
        return None, f"Для участка {aoi_id} нет базовой линии"

    row = row.iloc[0]
    series = simulate_biomass(row, year_start, year_end, cf)

    if len(series) < 2:
        return None, "Слишком короткий период для анализа"

    c_start = series[0]["carbon_t_ha"]
    c_end = series[-1]["carbon_t_ha"]
    delta_c = c_end - c_start

    return {
        "series": series,
        "c_start": c_start,
        "c_end": c_end,
        "delta_c": delta_c,
        "dt": year_end - year_start,
    }, None


def delta_c_to_co2(delta_c, area_ha):
    """ΔC (т C/га) → E (т CO2-экв) для всей площади."""
    return -delta_c * area_ha * (44 / 12)
