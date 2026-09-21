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

    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/"
              "World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr=".",
        name="Спутник",
        overlay=False,
        control=True,
        max_zoom=19,
    ).add_to(m)

    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/"
              "Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
        attr=".",
        name="Подписи",
        overlay=True,
        control=True,
        max_zoom=19,
    ).add_to(m)

    folium.Marker(
        [lat, lon],
        popup=f"<b>{name}</b><br>Площадь: {area_ha} га",
        tooltip=name,
        icon=folium.Icon(color="green", icon="tree", prefix="fa"),
    ).add_to(m)

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

    folium.LayerControl(collapsed=False).add_to(m)

    # === ВСТАВЛЯЕМ JS ВНУТРЬ КАРТЫ ===
    # Он выполняется в контексте iframe, где живёт Leaflet,
    # и физически удаляет плашку из DOM.
    kill_attribution_js = """
    <script>
    (function() {
        function killAttr() {
            var map = document.querySelector('.folium-map');
            if (!map || !map._leaflet_id) return;
            // Удаляем все control-attribution из DOM
            document.querySelectorAll(
                '.leaflet-control-attribution, .leaflet-bottom.leaflet-right'
            ).forEach(function(el) { el.remove(); });
        }
        // Пробуем несколько раз — Leaflet может грузиться асинхронно
        for (var i = 0; i < 30; i++) {
            setTimeout(killAttr, i * 100);
        }
        // И разово — через MutationObserver (если что-то добавится заново)
        var obs = new MutationObserver(killAttr);
        obs.observe(document.body, { childList: true, subtree: true });
    })();
    </script>
    """
    m.get_root().html.add_child(folium.Element(kill_attribution_js))

    st_folium(m, width=750, height=500, returned_objects=[])
