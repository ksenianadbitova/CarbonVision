import streamlit as st
import pandas as pd
from pathlib import Path

from modules.loader import (load_locations, load_biomass,
                            load_baseline, load_parameters, load_events)
from modules.carbon_calc import compute_carbon, delta_c_to_co2
from modules.uncertainty import scenario_uncertainty
from modules.credits_calc import compute_credits
from ui.map_view import render_map
from ui.charts import biomass_chart
from ui.money_view import render_money

# ---------- Настройка страницы ----------
st.set_page_config(
    page_title="CarbonVision",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Подключение CSS ----------
css_path = Path(__file__).parent / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>",
                unsafe_allow_html=True)

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
st.sidebar.markdown("""
<div style="text-align:center; padding: 0.5rem 0 1rem 0;">
    <div style="font-size: 2rem; line-height: 1;">🇷🇺</div>
    <h2 style="margin: 0.3rem 0 0.2rem 0; color: #1b4332; font-weight: 800;">
        CarbonVision
    </h2>
    <p style="color: #1b4332; font-size: 0.85rem; margin: 0;">
        Верификация углеродных кредитов<br>
        <b>Леса России</b>
    </p>
</div>
""", unsafe_allow_html=True)

aoi_options = {row["name"]: row for _, row in locations.iterrows()}
aoi_name = st.sidebar.selectbox("Локация", list(aoi_options.keys()))
aoi = aoi_options[aoi_name]

year_start = st.sidebar.slider("Начальный год", 2019, 2023, 2019)
year_end = st.sidebar.slider("Конечный год", year_start + 1, 2024, 2024)

run = st.sidebar.button("🚀 Анализировать", type="primary")

# ---------- Красивая шапка ----------
st.markdown("""
<div class="hero-banner fade-in">
    <h1>🌍 CarbonVision</h1>
    <p>🇷🇺 Верификация «зелёных» инвестиций и углеродных кредитов в лесах России</p>
    <div style="margin-top: 0.8rem;">
        <span class="badge">🇷🇺 Россия</span>
        <span class="badge">🛰️ ESA CCI Biomass</span>
        <span class="badge">🌲 Sentinel-2</span>
        <span class="badge">🔥 MODIS</span>
        <span class="badge">🌳 GFC</span>
    </div>
</div>

<div style="text-align: center; margin-bottom: 1.5rem;">
    <div class="status-bar">
        <span class="status-dot"></span>
        🇷🇺 Система активна • Данные по лесам России загружены
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)

# ---------- Карта + инфо ----------
col1, col2 = st.columns([1.5, 1])
with col1:
    st.markdown("""
    <div class="section-title">
        <span class="icon">🗺️</span>
        <span>Карта участка</span>
    </div>
    """, unsafe_allow_html=True)
    render_map(aoi["lat"], aoi["lon"], aoi["name"], aoi["area_ha"])
with col2:
    st.markdown("""
    <div class="section-title">
        <span class="icon">ℹ️</span>
        <span>Информация</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="info-card fade-in">
        <p class="label">🌍 Регион</p>
        <p class="value">{aoi['region']}</p>
    </div>

    <div class="info-card fade-in">
        <p class="label">📐 Площадь участка</p>
        <p class="value">{aoi['area_ha']} га</p>
    </div>

    <div class="info-card fade-in">
        <p class="label">📅 Период анализа</p>
        <p class="value">{year_start} – {year_end}</p>
    </div>

    <div class="info-card fade-in">
        <p class="label">🆔 Идентификатор</p>
        <p class="value">{aoi['aoi_id']}</p>
    </div>
    """, unsafe_allow_html=True)

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
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-title">
        <span class="icon">📊</span>
        <span>Результаты анализа</span>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🌱 Запас (начало)", f"{result['c_start']:.2f} т C/га")
    c2.metric("🌳 Запас (конец)", f"{result['c_end']:.2f} т C/га")
    c3.metric("📈 Δ Углерод", f"{result['delta_c']:+.2f} т C/га")
    c4.metric("💨 E (проект)", f"{E_project:+,.0f} т CO₂-экв".replace(",", " "))

    st.plotly_chart(biomass_chart(result["series"], aoi_name),
                    use_container_width=True)

    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-title">
        <span class="icon">📉</span>
        <span>Неопределённость и базовая линия</span>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("📏 Границы E",
              f"[{unc['L']:,.0f} ; {unc['U']:,.0f}]".replace(",", " "))
    c2.metric("🎯 E базовой линии",
              f"{E_baseline:+,.0f} т CO₂-экв".replace(",", " "))
    c3.metric("⚖️ H/R",
              f"{credits.get('H/R', 0):.2f}" if 'H/R' in credits else "—")

    # ---------- Потенциальные единицы ----------
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-title">
        <span class="icon">🌱</span>
        <span>Потенциальные углеродные единицы</span>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns([1, 2])
    with c1:
        st.metric("Q (единиц)", f"{credits['Q']:,}".replace(",", " "))
    with c2:
        status_color = "#52b788" if credits['Q'] > 0 else "#ffd166"
        st.markdown(f"""
        <div class="info-card">
            <p class="label">Статус расчёта</p>
            <p class="value" style="color: {status_color};">
                {credits['status']}
            </p>
        </div>
        """, unsafe_allow_html=True)

    if credits["Q"] > 0:
        with st.expander("🔍 Детали расчёта"):
            st.json({k: (round(v, 3) if isinstance(v, float) else v)
                     for k, v in credits.items()})

    # ---------- ДЕНЬГИ ----------
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    render_money(credits["Q"], prices)

    # ---------- События ----------
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-title">
        <span class="icon">🔥</span>
        <span>События на участке</span>
    </div>
    """, unsafe_allow_html=True)

    ev = events[events["aoi_id"] == aoi["aoi_id"]]
    if ev.empty:
        st.info("🌿 На этом участке событий не зафиксировано")
    else:
        st.dataframe(ev, use_container_width=True, hide_index=True)

    # ---------- Скачать отчёт ----------
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-title">
        <span class="icon">📥</span>
        <span>Экспорт отчёта</span>
    </div>
    """, unsafe_allow_html=True)

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