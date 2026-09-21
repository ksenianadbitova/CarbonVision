import pandas as pd


def compute_carbon(biomass_df, aoi_id, year_start, year_end, cf):
    """Считает средний и суммарный запас углерода на две даты."""
    sub = biomass_df[biomass_df["aoi_id"] == aoi_id].copy()
    sub = sub[(sub["year"] >= year_start) & (sub["year"] <= year_end)]

    if sub.empty:
        return None, "Нет данных биомассы за выбранный период"

    sub = sub.sort_values("year")
    sub["carbon_t_ha"] = sub["biomass_t_ha"] * cf

    c_start = float(sub.iloc[0]["carbon_t_ha"])
    c_end = float(sub.iloc[-1]["carbon_t_ha"])
    delta_c = c_end - c_start

    return {
        "series": sub[["year", "carbon_t_ha"]].to_dict("records"),
        "c_start": c_start,
        "c_end": c_end,
        "delta_c": delta_c,
        "dt": year_end - year_start,
    }, None


def delta_c_to_co2(delta_c, area_ha):
    """Перевод ΔC (т C/га) в E (т CO2-экв) на всей площади."""
    E = -delta_c * area_ha * (44 / 12)
    return E