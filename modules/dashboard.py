"""Streamlit dashboard compatibile con Streamlit < 1.22 (senza experimental_rerun).

- Auto‑refresh opzionale con pacchetto `streamlit_autorefresh` se presente.
- In mancanza, mostra un pulsante manuale "Aggiorna".
"""
import streamlit as st
import pandas as pd
from pathlib import Path
from importlib.util import find_spec

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = BASE_DIR / "trade_log.csv"

st.set_page_config(page_title="DotBot Dashboard", layout="wide", initial_sidebar_state="collapsed")
st.title("📊 DotBot – Dashboard Operativa")

REFRESH_SEC = 30
has_auto = False
if find_spec("streamlit_autorefresh"):
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=REFRESH_SEC*1000, key="datarefresh")
    has_auto = True

if has_auto:
    st.caption(f"⏱️ Auto‑refresh ogni {REFRESH_SEC}s")
else:
    st.caption("🔄 Auto‑refresh non disponibile – usa il pulsante qui sotto")
    if st.button("Aggiorna ora"):
        st.experimental_rerun()

# ---------------- Caricamento dati ---------------- #
if not LOG_FILE.exists():
    st.error("❌ trade_log.csv non trovato.")
    st.stop()

try:
    df = pd.read_csv(LOG_FILE)
except Exception as exc:
    st.error(f"Errore lettura CSV: {exc}")
    st.stop()

if df.empty:
    st.warning("⚠️ Il file trade_log.csv non contiene dati.")
    st.stop()

# ------------------- Layout ----------------------- #
st.subheader("📈 Storico Operazioni (ultime 50)")
st.dataframe(df.tail(50), height=300)

latest = df.iloc[-1]

def safe_metric(label, val):
    st.metric(label, val if pd.notna(val) else "—")

c1, c2, c3 = st.columns(3)
with c1:
    safe_metric("Prezzo", f"${latest.get('current_price', latest.get('Price', float('nan'))):.2f}")
    safe_metric("Forecast", f"${latest.get('forecast_price', latest.get('Forecast', float('nan'))):.2f}")
    safe_metric("Sentiment", f"{latest.get('sentiment', latest.get('Sentiment', float('nan'))):.2f}")

with c2:
    safe_metric("RSI", f"{latest.get('RSI', float('nan')):.2f}")
    safe_metric("MACDh", f"{latest.get('MACDh', float('nan')):.4f}")
    safe_metric("Trend", latest.get('trend', latest.get('Trend', '—')))

with c3:
    safe_metric("Azione", latest.get('action', latest.get('Action', '—')))
    safe_metric("DOT venduti", latest.get('dot_to_sell', '—'))
    safe_metric("Saldo DOT", latest.get('dot_balance', '—'))
