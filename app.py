import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from src.anomaly_detector import EnergyAnomalyDetector
from src.data_generator import generate_energy_data

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Mali Energy Anomaly Detector",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé
st.markdown("""
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #008751;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #6c757d;
        margin-bottom: 1.5rem;
    }
    .kpi-card {
        background-color: #1e293b;
        padding: 1.2rem;
        border-radius: 10px;
        border-left: 5px solid #008751;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .kpi-title {
        font-size: 0.9rem;
        color: #94a3b8;
        font-weight: 600;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #f8fafc;
    }
    </style>
""", unsafe_allow_html=True)

# Header de l'application
st.markdown('<div class="main-title">⚡ Mali Energy Anomaly Detector</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Plateforme IA de détection des anomalies & des pertes non-techniques de consommation électrique</div>', unsafe_allow_html=True)

# Barre latérale (Sidebar)
st.sidebar.header("⚙️ Paramètres & Modèle ML")

data_source = st.sidebar.radio(
    "Source des Données :",
    ["Dataset Exemple (Généré)", "Téléverser mon fichier CSV"]
)

if data_source == "Téléverser mon fichier CSV":
    uploaded_file = st.sidebar.file_uploader("Fichier CSV (horodatage, meter_id, consumption_kwh, voltage_v...)", type=["csv"])
    if uploaded_file is not None:
        df_raw = pd.read_csv(uploaded_file)
    else:
        st.info("📌 Veuillez téléverser un fichier CSV ou basculer sur le 'Dataset Exemple'.")
        df_raw = generate_energy_data(days=30, meters_count=5)
else:
    df_raw = generate_energy_data(days=45, meters_count=5)

contamination_rate = st.sidebar.slider(
    "Taux de Contamination Modèle (Taux d'Anomalies Estimé) :",
    min_value=0.01,
    max_value=0.15,
    value=0.05,
    step=0.01
)

tariff_per_kwh = st.sidebar.number_input(
    "Tarif de l'électricité (FCFA / kWh) :",
    min_value=50,
    max_value=300,
    value=120,
    step=5
)

# Execution du moteur de détection
detector = EnergyAnomalyDetector(contamination=contamination_rate)
df_processed = detector.fit_predict(df_raw)
kpis = detector.compute_summary_kpis(df_processed, price_per_kwh_xof=tariff_per_kwh)

# Filtre par Compteur
all_meters = ["Tous les compteurs"] + sorted(df_processed['meter_id'].unique().tolist())
selected_meter = st.sidebar.selectbox("Filtrer par Compteur :", all_meters)

if selected_meter != "Tous les compteurs":
    df_display = df_processed[df_processed['meter_id'] == selected_meter].copy()
else:
    df_display = df_processed.copy()

# Affichage des KPIs
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-title">TOTAL RELEVÉS</div>
            <div class="kpi-value">{len(df_display):,}</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    anom_count = len(df_display[df_display['is_detected_anomaly']])
    st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #ef4444;">
            <div class="kpi-title">ANOMALIES DÉTECTÉES</div>
            <div class="kpi-value" style="color: #ef4444;">{anom_count:,}</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    rate = (anom_count / len(df_display) * 100) if len(df_display) > 0 else 0
    st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #f59e0b;">
            <div class="kpi-title">TAUX D'ANOMALIE</div>
            <div class="kpi-value" style="color: #f59e0b;">{rate:.2f}%</div>
        </div>
    """, unsafe_allow_html=True)

with col4:
    susp_kwh = df_display[df_display['is_detected_anomaly']]['consumption_kwh'].sum()
    risk_fcfa = susp_kwh * tariff_per_kwh
    st.markdown(f"""
        <div class="kpi-card" style="border-left-color: #3b82f6;">
            <div class="kpi-title">RISQUE FINANCIER ÉVALUÉ</div>
            <div class="kpi-value" style="color: #3b82f6;">{risk_fcfa:,.0f} FCFA</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Graphique principal : Courbe de consommation + Anomalies
st.subheader("📈 Courbe de Consommation Temporelle & Anomalies Détectées")

fig_time = go.Figure()

# Courbe Normale
df_normal = df_display[~df_display['is_detected_anomaly']]
df_anom = df_display[df_display['is_detected_anomaly']]

fig_time.add_trace(go.Scatter(
    x=df_display['timestamp'],
    y=df_display['consumption_kwh'],
    mode='lines',
    name='Consommation (kWh)',
    line=dict(color='#0284c7', width=1.5),
    opacity=0.7
))

# Points d'anomalies en Rouge
fig_time.add_trace(go.Scatter(
    x=df_anom['timestamp'],
    y=df_anom['consumption_kwh'],
    mode='markers',
    name='Anomalie / Fraude Suspecte',
    marker=dict(color='#ef4444', size=8, symbol='x-open'),
    hovertemplate="<b>Date</b>: %{x}<br><b>Consommation</b>: %{y} kWh<extra></extra>"
))

fig_time.update_layout(
    template="plotly_dark",
    height=420,
    margin=dict(l=20, r=20, t=30, b=20),
    xaxis_title="Horodatage",
    yaxis_title="Consommation (kWh)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig_time, use_container_width=True)

# Deuxième rangée de graphiques
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("⚡ Tension vs Consommation (Anomalies)")
    fig_scatter = px.scatter(
        df_display,
        x="voltage_v",
        y="consumption_kwh",
        color="is_detected_anomaly",
        color_discrete_map={True: '#ef4444', False: '#10b981'},
        labels={'is_detected_anomaly': 'Est Anormal', 'voltage_v': 'Tension (V)', 'consumption_kwh': 'Consommation (kWh)'},
        hover_data=['meter_id', 'anomaly_score'],
        template="plotly_dark"
    )
    fig_scatter.update_layout(height=350, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_scatter, use_container_width=True)

with col_right:
    st.subheader("📊 Distribution du Score d'Anomalie ML")
    fig_hist = px.histogram(
        df_display,
        x="anomaly_score",
        nbins=40,
        color="is_detected_anomaly",
        color_discrete_map={True: '#ef4444', False: '#0284c7'},
        labels={'anomaly_score': "Score d'Anomalie (0 à 1)"},
        template="plotly_dark"
    )
    fig_hist.update_layout(height=350, margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig_hist, use_container_width=True)

# Tableau détaillé des anomalies
st.subheader("🚨 Journal Détaillé des Relevés Anormaux")
if len(df_anom) > 0:
    st.dataframe(
        df_anom[['timestamp', 'meter_id', 'consumption_kwh', 'voltage_v', 'current_a', 'power_factor', 'anomaly_score']]
        .sort_values(by='anomaly_score', ascending=False),
        use_container_width=True,
        hide_index=True
    )
    
    # Export CSV
    csv_data = df_anom.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Télécharger le Rapport d'Anomalies (CSV)",
        data=csv_data,
        file_name=f"rapport_anomalies_energie_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        mime="text/csv"
    )
else:
    st.success("✅ Aucune anomalie détectée selon le seuil sélectionné.")
