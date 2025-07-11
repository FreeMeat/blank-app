import streamlit as st
import requests
from bs4 import BeautifulSoup
import random
import time
from datetime import datetime

# Konfiguration
st.set_page_config(
    page_title="🚀 Value Investor Pro",
    layout="centered",
    page_icon="💹"
)

# Chrome-Einstellungen
CHROME_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Accept-Language': 'de-DE,de;q=0.9',
    'Referer': 'https://www.google.com/'
}

def get_data(isin):
    try:
        url = f"https://www.onvista.de/aktien/{isin}"
        response = requests.get(
            url,
            headers=CHROME_HEADERS,
            timeout=15,
            proxies={"http": None, "https": None}  # Proxy deaktivieren
        )
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Daten extrahieren
        name = soup.find('h1', class_='headline').get_text(strip=True)
        price = soup.find('span', class_='price').get_text(strip=True)
        
        metrics = {
            "KGV": soup.find('td', text=lambda t: t and "KGV (aktuell)" in t).find_next_sibling('td').get_text(strip=True),
            "KBV": soup.find('td', text="KBV").find_next_sibling('td').get_text(strip=True),
            "Dividende": soup.find('td', text="Dividendenrendite").find_next_sibling('td').get_text(strip=True)
        }
        
        return {
            "Name": name,
            "Preis": price,
            **metrics
        }
        
    except Exception as e:
        st.error(f"Fehler: {str(e)}")
        return None

# UI
st.title("📊 Value Investing Analyzer")
st.markdown("""
<style>
.stTextInput>div>div>input {font-size: 16px !important;}
.stButton>button {background-color: #4CAF50 !important; color: white !important;}
</style>
""", unsafe_allow_html=True)

isin = st.text_input("ISIN eingeben (z.B. DE000BASF111):", "DE000BASF111")

if st.button("Analyse starten"):
    with st.spinner("Daten werden abgerufen..."):
        data = get_data(isin)
        time.sleep(1)  # Gegen Blockierung
        
    if data:
        st.success(f"**{data['Name']}**")
        
        col1, col2 = st.columns(2)
        col1.metric("Aktueller Preis", data["Preis"])
        col2.metric("Dividendenrendite", data["Dividende"])
        
        st.write(f"""
        - **KGV:** {data["KGV"]}
        - **KBV:** {data["KBV"]}
        """)
        
        st.caption(f"Stand: {datetime.now().strftime('%d.%m.%Y %H:%M')}")

st.markdown("---")
st.info("ℹ️ Bei Blockierungen: VPN aktivieren oder 5 Minuten warten.")
