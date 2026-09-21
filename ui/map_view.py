import folium
from streamlit_folium import st_folium
import streamlit as st


def render_map(lat, lon, name, area_ha):
    m = folium.Map(
        location=[lat, lon],
        zoom_start=12,
        tiles=None,
        control_scale=True,
    )

    # Спутник Esri World Imagery
    # attr непустой (требование Folium), но визуально скрываем через CSS
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/"
              "World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr=" ",
        name="Спутник",
        overlay=False,
        control=True,
        max_zoom=19,
    ).add_to(m)

    # Слой подписей
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/"
              "Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
        attr=" ",
        name="Подписи",
        overlay=True,
        control=True,
        max_zoom=19,
    ).add_to(m)

    # Маркер участка
    folium.Marker(
        [lat, lon],
        popup=f"<b>{name}</b><br>Площадь: {area_ha} га",
        tooltip=name,
        icon=folium.Icon(color="green", icon="tree", prefix="fa"),
    ).add_to(m)

    # Контур участка
    folium.Circle(
        [lat, lon],
        radius=3000,
        color="#2d6a4f",
        fill=True,
        fill_color="#52b788",
        fill_opacity=0.25,
        weight=3,
        tooltip=f"{name} — {area_ha} га",
    ).add_to(m)

    # Переключатель слоёв
    folium.LayerControl(collapsed=False).add_to(m)

    st_folium(m, width=750, height=500, returned_objects=[])

    # CSS: полностью скрываем атрибуцию Leaflet/Esri
    st.markdown("""
    <style>
        .leaflet-control-attribution,
        .leaflet-bottom.leaflet-right,
        .leaflet-control-attribution * {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            height: 0 !important;
            width: 0 !important;
        }
    </style>
    """, unsafe_allow_html=True)
