import folium
import streamlit as st
import streamlit.components.v1 as components


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
        attr="©",
        name="Спутник",
        overlay=False,
        control=True,
        max_zoom=19,
    ).add_to(m)

    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/"
              "Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}",
        attr="©",
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

    # Получаем HTML-строку карты
    map_html = m.get_root().render()

    # CSS вставляем ПЕРЕД </head>, JS — ПЕРЕД </body>
    css_injection = """
    <style>
        .leaflet-control-attribution,
        .leaflet-bottom.leaflet-right,
        .leaflet-control-attribution * {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            width: 0 !important;
            height: 0 !important;
            pointer-events: none !important;
        }
    </style>
    """
    map_html = map_html.replace("</head>", css_injection + "</head>")

    js_injection = """
    <script>
    (function() {
        function kill() {
            document.querySelectorAll(
                '.leaflet-control-attribution, .leaflet-bottom.leaflet-right'
            ).forEach(function(el) { el.remove(); });
        }
        setInterval(kill, 250);
    })();
    </script>
    """
    map_html = map_html.replace("</body>", js_injection + "</body>")

    # Рендерим карту напрямую через components.html
    components.html(map_html, height=520, scrolling=False)
