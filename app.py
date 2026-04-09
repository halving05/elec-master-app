import streamlit as st
import pandas as pd
import sqlite3
import os

# --- CONFIGURATION DES PARTS ---
PART_1, PART_2, PART_3 = 0.40, 0.30, 0.30

# --- FONCTIONS BASE DE DONNÉES ---
def init_db():
    conn = sqlite3.connect('elec_master_v2.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS stock 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  nom TEXT, qte INTEGER, p_achat REAL, p_vente REAL)''')
    conn.commit()
    return conn

conn = init_db()

# --- INTERFACE ---
st.set_page_config(page_title="Elec Master Tech Pro", layout="wide")
st.title("⚡ Elec Master Tech : Gestion de Vente")

menu = ["Tableau de Bord", "Ajouter Stock", "Parts Associés"]
choix = st.sidebar.radio("Navigation", menu)

if choix == "Ajouter Stock":
    st.subheader("📦 Enregistrer un achat")
    with st.form("ajout"):
        nom = st.text_input("Nom de l'article")
        qte = st.number_input("Quantité", min_value=1)
        pa = st.number_input("Prix d'achat unitaire (CFA)", min_value=0.0)
        pv = st.number_input("Prix de vente unitaire (CFA)", min_value=0.0)
        if st.form_submit_button("Enregistrer"):
            c = conn.cursor()
            c.execute("INSERT INTO stock (nom, qte, p_achat, p_vente) VALUES (?,?,?,?)", (nom, qte, pa, pv))
            conn.commit()
            st.success(f"{nom} ajouté au stock !")

elif choix == "Tableau de Bord":
    st.subheader("📊 Bilan Financier")
    df = pd.read_sql_query("SELECT * FROM stock", conn)
    if not df.empty:
        df['Total Achat'] = df['qte'] * df['p_achat']
        df['Total Vente'] = df['qte'] * df['p_vente']
        df['Bénéfice'] = df['Total Vente'] - df['Total Achat']
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Capital Investi", f"{df['Total Achat'].sum():,.0f} CFA")
        col2.metric("Chiffre d'Affaires", f"{df['Total Vente'].sum():,.0f} CFA")
        col3.metric("Bénéfice Total", f"{df['Bénéfice'].sum():,.0f} CFA")
        
        st.write("### Détails des articles")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Aucune donnée disponible.")

elif choix == "Parts Associés":
    st.subheader("👥 Répartition des Bénéfices")
    df = pd.read_sql_query("SELECT * FROM stock", conn)
    if not df.empty:
        total_benef = (df['qte'] * (df['p_vente'] - df['p_achat'])).sum()
        st.write(f"### Bénéfice net à partager : *{total_benef:,.0f} CFA*")
        
        c1, c2, c3 = st.columns(3)
        c1.warning(f"Associé 1 (40%)\n\n*{total_benef * PART_1:,.0f} CFA*")
        c2.info(f"Associé 2 (30%)\n\n*{total_benef * PART_2:,.0f} CFA*")
        c3.info(f"Associé 3 (30%)\n\n*{total_benef * PART_3:,.0f} CFA*")
