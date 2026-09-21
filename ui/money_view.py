import streamlit as st
import plotly.express as px
import pandas as pd


def render_money(Q, prices):
    st.markdown("""
    <h2 style="text-align:center;">💰 Потенциальный доход</h2>
    """, unsafe_allow_html=True)

    if Q <= 0:
        st.warning("Углеродные единицы не рассчитаны — доход = 0 ₽")
        return

    cols = st.columns(3)
    labels = ["🟢 Пессимистичный", "🟡 Базовый", "🔵 Оптимистичный"]
    keys = ["price_low", "price_mid", "price_high"]
    colors = ["#52b788", "#ffd166", "#4cc9f0"]

    data = []
    for col, label, key, color in zip(cols, labels, keys, colors):
        price = float(prices[key])
        revenue = Q * price
        with col:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, {color}22, {color}44);
                border: 1px solid {color};
                border-radius: 18px;
                padding: 1.2rem;
                text-align: center;
                backdrop-filter: blur(8px);
                transition: transform 0.2s ease;
            ">
                <p style="color: {color}; font-size: 1rem;
                          margin: 0 0 0.4rem 0; font-weight: 600;">
                    {label}
                </p>
                <p style="font-size: 1.8rem; color: #e8f5e9;
                          font-weight: 800; margin: 0.2rem 0;">
                    {revenue:,.0f} ₽
                </p>
                <p style="color: #95d5b2; font-size: 0.85rem; margin: 0;">
                    {price:.0f} ₽/ед
                </p>
            </div>
            """.replace(",", " "), unsafe_allow_html=True)
        data.append({"Сценарий": label, "Доход (₽)": revenue})

    st.markdown("<br>", unsafe_allow_html=True)

    df = pd.DataFrame(data)
    fig = px.bar(
        df, x="Сценарий", y="Доход (₽)", color="Сценарий",
        color_discrete_sequence=colors,
        title="Доход по трём сценариям цены",
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8f5e9", size=14),
        title_font=dict(color="#b7e4c7", size=18),
        showlegend=False,
        margin=dict(l=20, r=20, t=60, b=20),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="rgba(149,213,178,0.15)")
    st.plotly_chart(fig, use_container_width=True)