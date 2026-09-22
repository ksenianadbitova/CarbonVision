import streamlit as st
import pandas as pd
from pathlib import Path

from modules.loader import (load_locations, load_baseline,
                            load_parameters, load_events)
from modules.carbon_calc import compute_carbon, delta_c_to_co2
from modules.uncertainty import scenario_uncertainty
from modules.credits_calc import compute_credits
from ui.map_view import render_map
from ui.charts import biomass_chart
from ui.money_view import render_money

st.set_page_config(
    page_title="Углеродные единицы",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------- CSS ----------
css_path = Path(__file__).parent / "assets" / "style.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text(encoding='utf-8')}</style>",
                unsafe_allow_html=True)

# ---------- Загрузка данных ----------
locations, err1 = load_locations()
baseline, err2 = load_baseline()
prices, err3 = load_parameters()
events, err4 = load_events()

errors = [e for e in [err1, err2, err3, err4] if e]
if errors:
    st.error("Не удалось загрузить данные:")
    for e in errors:
        st.write("—", e)
    st.stop()

# ---------- Считаем метрики по всем участкам ----------
cf = float(prices.get("CF_AGB", 0.47))

rows = []
total_units = 0
total_area = 0.0

for _, aoi in locations.iterrows():
    try:
        result, err = compute_carbon(baseline, aoi["aoi_id"], 2019, 2024, cf)
        if err:
            continue

        E_project = delta_c_to_co2(result["delta_c"], aoi["area_ha"])

        base_row = baseline[baseline["aoi_id"] == aoi["aoi_id"]]
        if base_row.empty:
            continue
        g = float(base_row.iloc[0]["g_tC_ha_yr"])
        base_start = float(base_row.iloc[0]["baseline_2019_tC_ha"])
        base_end = base_start + g * 5
        E_baseline = -((base_end - base_start) * aoi["area_ha"] * (44 / 12))

        unc = scenario_uncertainty(E_project)

        LK = float(prices.get("LK", 0))
        credits = compute_credits(E_project, E_baseline, LK, unc["H"])

        Q = credits.get("Q", 0)
        total_units += Q
        total_area += float(aoi["area_ha"])

        rows.append({
            "Участок": aoi["aoi_id"],
            "Регион": aoi["region"],
            "Площадь, га": round(float(aoi["area_ha"]), 2),
            "Запас 2019, т C/га": round(result["c_start"], 2),
            "Запас 2024, т C/га": round(result["c_end"], 2),
            "ΔC, т C": round(result["delta_c"] * aoi["area_ha"], 0),
            "CO₂-экв., т": round(E_project, 0),
            "Единицы (Q)": Q,
        })
    except Exception as e:
        st.warning(f"Ошибка на участке {aoi.get('aoi_id', '?')}: {e}")
        continue

# ---------- Шапка ----------
st.markdown(f"""
<div class="hero-section">
    <div class="hero-top">
        <span class="hero-logo">🌱 Углеродные единицы</span>
        <span class="hero-nav">
            <a href="#map">Карта</a>
            <a href="#metrics">Метрики</a>
            <a href="#about">О проекте</a>
        </span>
    </div>
    <div class="hero-body">
        <h1>Найдите, где купить, держать или создать свою углеродную ферму</h1>
        <p>Спутниковая верификация «зелёных» инвестиций по данным ESA CCI Biomass, Sentinel-2, GFC и MODIS</p>
        <div class="hero-stats">
            <div class="hero-stat">
                <div class="hero-stat-value">{len(locations)}</div>
                <div class="hero-stat-label">Участка</div>
            </div>
            <div class="hero-stat">
                <div class="hero-stat-value">{int(total_area):,}</div>
                <div class="hero-stat-label">Гектаров</div>
            </div>
            <div class="hero-stat">
                <div class="hero-stat-value">{total_units:,}</div>
                <div class="hero-stat-label">Углеродный единиц</div>
            </div>
            <div class="hero-stat">
                <div class="hero-stat-value">{total_units * 1500:,} ₽</div>
                <div class="hero-stat-label">Рублей потенциала</div>
            </div>
        </div>
    </div>
</div>
""".replace(",", " "), unsafe_allow_html=True)

# ---------- Карта ----------
st.markdown('<div id="map"></div>', unsafe_allow_html=True)
st.markdown("### 🗺️ Карта участков")

selected_name = st.selectbox(
    "Выберите участок",
    options=locations["name"].tolist(),
    index=0,
)
selected = locations[locations["name"] == selected_name].iloc[0]

render_map(
    float(selected["lat"]),
    float(selected["lon"]),
    selected["name"],
    float(selected["area_ha"]),
)

# ---------- 3 метрики ----------
st.markdown('<div id="metrics"></div>', unsafe_allow_html=True)
st.markdown("### Три метрики для инвестора")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="metric-card metric-buy">
        <div class="metric-icon">🛒</div>
        <h3>Покупать</h3>
        <p>Для промышленных предприятий, которые хотят минимизировать экологические последствия своей деятельности</p>
        <div class="metric-value">0 ед.</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card metric-hold">
        <div class="metric-icon">📦</div>
        <h3>Держать</h3>
        <p>Для тех, у кого уже есть лес — заповедники, ООПТ, частные владельцы. Заработок без вырубок</p>
        <div class="metric-value">0 ед.</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card metric-create">
        <div class="metric-icon">🌳</div>
        <h3>Создать ферму</h3>
        <p>Подобрать место с бесхозным лесом или выращивать свой собственный лес</p>
        <div class="metric-value">0 ед.</div>
    </div>
    """, unsafe_allow_html=True)

# ---------- Таблица ----------
st.markdown("### Детальные данные по участкам")

if rows:
    df_table = pd.DataFrame(rows)
    st.dataframe(df_table, use_container_width=True, hide_index=True)
else:
    st.info("Нет данных для отображения")

# ---------- Расчёт для выбранного ----------
result, err = compute_carbon(baseline, selected["aoi_id"], 2019, 2024, cf)
if err:
    st.warning(f"⚠️ {err}")
else:
    E_project = delta_c_to_co2(result["delta_c"], selected["area_ha"])

    base_row = baseline[baseline["aoi_id"] == selected["aoi_id"]]
    g = float(base_row.iloc[0]["g_tC_ha_yr"])
    base_start = float(base_row.iloc[0]["baseline_2019_tC_ha"])
    base_end = base_start + g * 5
    E_baseline = -((base_end - base_start) * selected["area_ha"] * (44 / 12))

    unc = scenario_uncertainty(E_project)
    LK = float(prices.get("LK", 0))
    credits = compute_credits(E_project, E_baseline, LK, unc["H"])

    st.markdown(f"### 📊 {selected['name']}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Запас 2019", f"{result['c_start']:.2f} т C/га")
    c2.metric("Запас 2024", f"{result['c_end']:.2f} т C/га")
    c3.metric("Δ углерода", f"{result['delta_c']:+.2f} т C/га")
    c4.metric("E (проект)", f"{E_project:+,.0f} т CO₂-экв".replace(",", " "))

    st.plotly_chart(biomass_chart(result["series"], selected["name"]),
                    use_container_width=True)

    st.markdown("### 🌱 Потенциальные углеродные единицы")
    st.metric("Q (единиц)", f"{credits.get('Q', 0):,}".replace(",", " "))
    st.caption(f"Статус: {credits.get('status', '—')}")

    st.markdown("---")
    render_money(credits.get("Q", 0), prices)

# ---------- О проекте ----------
st.markdown('<div id="about"></div>', unsafe_allow_html=True)
st.markdown("### О проекте")

a1, a2 = st.columns(2)
with a1:
    st.markdown("""
    <div class="about-card">
        <div class="about-icon">📖</div>
        <h4>Научная основа</h4>
        <p>Расчёт по методике МГЭИК (IPCC 2006), коэффициент CF = 0.47, метод разности запасов (stock-difference)</p>
    </div>
    <div class="about-card">
        <div class="about-icon">📊</div>
        <h4>Точность</h4>
        <p>Учёт неопределённости, вычет 10%, резерв 15%, округление вниз</p>
    </div>
    """, unsafe_allow_html=True)

with a2:
    st.markdown("""
    <div class="about-card">
        <div class="about-icon">🛰️</div>
        <h4>Данные</h4>
        <p>ESA CCI Biomass v7.0, Sentinel-2 L2A, Hansen GFC 2025 v1.13, MODIS MCD64A1 v6.1</p>
    </div>
    <div class="about-card">
        <div class="about-icon">💡</div>
        <h4>Дополнительно</h4>
        <p>Рекреационный потенциал, объединение с экотуризмом для дополнительной прибыли</p>
    </div>
    """, unsafe_allow_html=True)

# ---------- Футер ----------
st.markdown("""
<div class="footer-note">
    Космохакатон 2026 • Кейс SR Data • Верификация углеродных кредитов<br>
    <small>Данные носят сценарный характер. Не являются сертифицированными углеродными единицами.</small>
</div>
""", unsafe_allow_html=True)
