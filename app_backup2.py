import streamlit as st
import pandas as pd

from modules.loader import (load_locations, load_biomass,
                            load_baseline, load_parameters, load_events)
from modules.carbon_calc import compute_carbon, delta_c_to_co2
from modules.uncertainty import scenario_uncertainty
from modules.credits_calc import compute_credits
from ui.map_view import render_map
from ui.charts import biomass_chart
from ui.money_view import render_money

st.set_page_config(page_title="CarbonVision", page_icon="🌍", layout="wide")

# ---------- Подключение CSS ----------
from pathlib import Path
css_path = Path(__file__).parent / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>",
                unsafe_allow_html=True)

# ---------- Настройка страницы ----------
st.set_page_config(
    page_title="CarbonVision",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Подключение CSS ----------
from pathlib import Path
css_path = Path(__file__).parent / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>",
                unsafe_allow_html=True)

# ---------- Подключение CSS ----------
css_path = Path(__file__).parent / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>",
                unsafe_allow_html=True)

# ---------- Красивый заголовок ----------
st.markdown("""
<div style="text-align: center; padding: 1rem 0 0.5rem 0;">
    <h1 style="font-size: 3rem; margin-bottom: 0.2rem;">
        🌍 CarbonVision
    </h1>
    <p style="color: #95d5b2; font-size: 1.1rem; margin-top: 0;">
        Верификация «зелёных» инвестиций и углеродных кредитов
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ---------- Загрузка данных с защитой ----------
locations, err1 = load_locations()
biomass, err2 = load_biomass()
baseline, err3 = load_baseline()
prices, err4 = load_parameters()
events, err5 = load_events()

errors = [e for e in [err1, err2, err3, err4, err5] if e]
if errors:
    st.error("Не удалось загрузить данные:")
    for e in errors:
        st.write("—", e)
    st.stop()

if locations is None or locations.empty:
    st.error("Файл локаций пуст. Проверьте data/locations.csv")
    st.stop()

# ---------- Сайдбар ----------
st.sidebar.title("🌍 CarbonVision")
st.sidebar.caption("Верификация углеродных кредитов")

aoi_options = {row["name"]: row for _, row in locations.iterrows()}
aoi_name = st.sidebar.selectbox("Локация", list(aoi_options.keys()))
aoi = aoi_options[aoi_name]

year_start = st.sidebar.slider("Начальный год", 2019, 2023, 2019)
year_end = st.sidebar.slider("Конечный год", year_start + 1, 2024, 2024)

run = st.sidebar.button("🚀 Анализировать", type="primary")

# ---------- Заголовок ----------
st.title("🌍 CarbonVision — верификация углеродных кредитов")
st.caption("Данные: ESA CCI Biomass (симуляция), Sentinel-2, GFC, MODIS")

# ---------- Карта + инфо ----------
col1, col2 = st.columns([1, 1])
with col1:
    st.subheader("📍 Карта участка")
    render_map(aoi["lat"], aoi["lon"], aoi["name"], aoi["area_ha"])
with col2:
    st.subheader("ℹ️ Информация")
    st.write(f"**Регион:** {aoi['region']}")
    st.write(f"**Площадь:** {aoi['area_ha']} га")
    st.write(f"**Период:** {year_start}–{year_end}")

# ---------- Расчёт ----------
if run:
    if aoi["area_ha"] <= 0:
        st.error("Площадь должна быть больше 0")
        st.stop()
    if year_end <= year_start:
        st.error("Конечный год должен быть больше начального")
        st.stop()

    cf = float(prices.get("CF_AGB", 0.47))

    result, err = compute_carbon(biomass, aoi["aoi_id"],
                                 year_start, year_end, cf)
    if err:
        st.warning(f"⚠️ {err}")
        st.info("Попробуйте выбрать другой период или локацию.")
        st.stop()

    E_project = delta_c_to_co2(result["delta_c"], aoi["area_ha"])

    base_row = baseline[baseline["aoi_id"] == aoi["aoi_id"]]
    if base_row.empty:
        st.warning("Для этой локации нет базовой линии")
        st.stop()

    g = float(base_row.iloc[0]["g_tC_ha_yr"])
    base_start = float(base_row.iloc[0]["baseline_2019_tC_ha"])
    base_end = base_start + g * (year_end - year_start)
    E_baseline = -((base_end - base_start) * aoi["area_ha"] * (44 / 12))

    unc = scenario_uncertainty(E_project)

    LK = float(prices.get("LK", 0))
    credits = compute_credits(E_project, E_baseline, LK, unc["H"])

    # ---------- Результаты ----------
    st.divider()
    st.subheader("📊 Результаты")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Средний запас (начало)", f"{result['c_start']:.2f} т C/га")
    c2.metric("Средний запас (конец)", f"{result['c_end']:.2f} т C/га")
    c3.metric("Изменение углерода", f"{result['delta_c']:+.2f} т C/га")
    c4.metric("E (проект)", f"{E_project:+,.0f} т CO₂-экв".replace(",", " "))

    st.plotly_chart(biomass_chart(result["series"], aoi_name),
                    use_container_width=True)

    st.subheader("📉 Неопределённость и базовый сценарий")
    c1, c2, c3 = st.columns(3)
    c1.metric("Границы E",
              f"[{unc['L']:,.0f} ; {unc['U']:,.0f}]".replace(",", " "))
    c2.metric("E базовой линии",
              f"{E_baseline:+,.0f} т CO₂-экв".replace(",", " "))
    c3.metric("H/R",
              f"{credits.get('H/R', 0):.2f}" if 'H/R' in credits else "—")

    st.divider()
    st.subheader("🌱 Потенциальные углеродные единицы")
    st.write(f"**Статус:** {credits['status']}")
    st.metric("Q (единиц)", f"{credits['Q']:,}".replace(",", " "))

    if credits["Q"] > 0:
        with st.expander("Детали расчёта"):
            st.json({k: (round(v, 3) if isinstance(v, float) else v)
                     for k, v in credits.items()})

    # ---------- ДЕНЬГИ ----------
    st.divider()
    render_money(credits["Q"], prices)

    # ---------- События ----------
    st.divider()
    st.subheader("🔥 События на участке")
    ev = events[events["aoi_id"] == aoi["aoi_id"]]
    if ev.empty:
        st.info("Событий не зафиксировано")
    else:
        st.dataframe(ev, use_container_width=True)

    # ---------- Скачать отчёт ----------
    st.divider()
    report = pd.DataFrame([{
        "aoi_id": aoi["aoi_id"],
        "name": aoi["name"],
        "period": f"{year_start}-{year_end}",
        "area_ha": aoi["area_ha"],
        "E_project": round(E_project, 2),
        "E_baseline": round(E_baseline, 2),
        "Q": credits["Q"],
        "revenue_low": credits["Q"] * float(prices["price_low"]),
        "revenue_mid": credits["Q"] * float(prices["price_mid"]),
        "revenue_high": credits["Q"] * float(prices["price_high"]),
    }])
    st.download_button("📥 Скачать отчёт (CSV)",
                       report.to_csv(index=False).encode("utf-8-sig"),
                       file_name=f"report_{aoi['aoi_id']}.csv",
                       mime="text/csv")
else:
    st.info("👈 Выберите параметры слева и нажмите **Анализировать**")