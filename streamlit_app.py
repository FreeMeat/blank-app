import streamlit as st
import requests
from bs4 import BeautifulSoup
import random
import time
from datetime import datetime

# ---------------------------
# KONFIGURATION
# ---------------------------
st.set_page_config(
    page_title="💰 Value Investor Pro (Chrome-Optimiert)",
    page_icon="📊",
    layout="centered"
)

# ---------------------------
# PROXY & CHROME-EINSTELLUNGEN
# ---------------------------
PROXY_SETTINGS = {
    "http": None,  # Proxy deaktivieren
    "https": None
}

CHROME_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
]

# ---------------------------
# FUNKTIONEN
# ---------------------------
def get_chrome_request(url, max_retries=3):
    """Sendet Chrome-ähnliche Requests mit Proxy-Umgehung"""
    for attempt in range(max_retries):
        try:
            headers = {
                'User-Agent': random.choice(CHROME_USER_AGENTS),
                'Accept-Language': 'de-DE,de;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Referer': 'https://www.google.com/'
            }
            
            response = requests.get(
                url,
                headers=headers,
                proxies=PROXY_SETTINGS,
                timeout=15
            )
            response.raise_for_status()
            return response
            
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponentielle Backoff-Strategie

def extract_financial_data(soup):
    """Extrahiert Finanzkennzahlen aus der OnVista-Seite"""
    data = {
        "name": soup.find('h1', class_='headline').get_text(strip=True) if soup.find('h1', class_='headline') else "N/A",
        "price": soup.find('span', class_='price').get_text(strip=True).replace(',', '.') if soup.find('span', class_='price') else "0.0",
        "metrics": {}
    }
    
    metrics_to_extract = {
        "KGV": "KGV (aktuell)",
        "KBV": "KBV",
        "KUV": "KUV",
        "Dividendenrendite": "Dividendenrendite",
        "Eigenkapitalrendite": "Eigenkapitalrendite"
    }
    
    for metric, onvista_key in metrics_to_extract.items():
        element = soup.find('td', text=lambda t: t and onvista_key in t)
        data["metrics"][metric] = element.find_next_sibling('td').get_text(strip=True) if element else "N/A"
    
    return data

# ---------------------------
# STREAMLIT UI
# ---------------------------
st.title("💰 Value Investor Pro")
st.markdown("""
<style>
    .stTextInput input {font-size: 16px !important;}
    .stButton>button {background-color: #4CAF50; color: white;}
    .metric-card {border-radius: 10px; padding: 15px; background: #f0f2f6; margin: 10px 0;}
</style>
""", unsafe_allow_html=True)

# ISIN-Eingabe
isin = st.text_input(
    "**ISIN eingeben** (z.B. DE000BASF111):",
    value="DE000BASF111",
    max_chars=12,
    placeholder="DE000BASF111"
)

if st.button("🚀 Analyse starten", type="primary"):
    if not isin:
        st.warning("Bitte eine ISIN eingeben!")
    else:
        with st.spinner("Daten werden über Chrome-Request abgerufen..."):
            try:
                # OnVista-Abruf
                url = f"https://www.onvista.de/aktien/{isin}"
                response = get_chrome_request(url)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Daten verarbeiten
                data = extract_financial_data(soup)
                
                # Ergebnisse anzeigen
                st.success(f"**{data['name']}**")
                
                # Metriken in Karten
                cols = st.columns(2)
                with cols[0]:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>Preis</h3>
                        <h2>{data['price']} €</h2>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>KGV</h3>
                        <h2>{data['metrics']['KGV']}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                with cols[1]:
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>Dividendenrendite</h3>
                        <h2>{data['metrics']['Dividendenrendite']}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                    <div class="metric-card">
                        <h3>KBV</h3>
                        <h2>{data['metrics']['KBV']}</h2>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Zeitstempel
                st.caption(f"Letzte Aktualisierung: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
                
            except Exception as e:
                st.error(f"""
                **Fehler beim Abruf der Daten:**
                ```
                {str(e)}
                ```
                Versuchen Sie es später erneut oder nutzen Sie eine VPN-Verbindung.
                """)

# Footer
st.markdown("---")
st.markdown("""
ℹ️ **Tipps für beste Ergebnisse:**
1. Bei Blockierungen 1-2 Minuten warten
2. VPN-Verbindung nutzen (z.B. Windscribe)
3. Alternative ISINs testen
""")
