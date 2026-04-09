import streamlit as st
import pandas as pd
import sqlite3
import os

# --- CONFIGURATION SÉCURITÉ ---
MOT_DE_PASSE = "elec2026" 

# --- CONFIGURATION DES PARTS (MISE À JOUR) ---
# Associé 1 : 20% | Associé 2 : 40% | Associé 3 : 40%
PART_1, PART_2, PART_3 = 0.20, 0.40, 0.40

# --- FONCTIONS BASE DE DONNÉES ---
def init_db():
    conn = sqlite3.connect('elec_master_v4.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS stock 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  nom TEXT, qte INTEGER, p_achat REAL, p_vente REAL)''')
    conn.commit()
    return conn

conn = init_db()

# --- VÉRIFICATION DE LA CONNEXION ---
if 'authentifie' not in st.session_state:
    st.session_state['authentifie'] = False

def check_password():
    if not st.session_state['authentifie']:
        st.title("🔐 Accès Sécurisé - Elec Master Tech")
        pwd = st.text_input("Entrez le code secret de l'entreprise", type="password")
        if st.button("Se connecter"):
            if pwd == MOT_DE_PASSE:
                st.session_state['authentifie'] = True
                st.rerun()
            else:
                st.error("Code incorrect ❌")
        return False
    return True

# --- INTERFACE PRINCIPALE ---
if check_password():
    st.set_page_config(page_title="Elec Master Tech Pro", layout="wide")
    
    if st.sidebar.button("Se déconnecter"):
        st.session_state['authentifie'] = False
        st.rerun()

    st.title("⚡ Elec Master Tech : Gestion & Parts")
    
    menu = ["Tableau de Bord", "Ajouter Stock", "Parts Associés"]
    choix = st.sidebar.radio("Navigation", menu)

    if choix == "Ajouter Stock":
        st.subheader("📦 Enregistrer du matériel")
        with st.form("ajout"):
            nom = st.text_input("Nom de l'article")
            qte = st.number_input("Quantité", min_value=1)
            pa = st.number_input("Prix d'achat unitaire (CFA)", min_value=0.0)
            pv = st.number_input("Prix de vente unitaire (CFA)", min_value=0.0)
            if st.form_submit_button("Enregistrer"):
                c = conn.cursor()
                c.execute("INSERT INTO stock (nom, qte, p_achat, p_vente) VALUES (?,?,?,?)", (nom, qte, pa, pv))
                conn.commit()
                st.success(f"L'article '{nom}' a été ajouté avec succès !")

    elif choix == "Tableau de Bord":
        st.subheader("📊 Bilan Financier Global")
        df = pd.read_sql_query("SELECT * FROM stock", conn)
        if not df.empty:
            df['Total Achat'] = df['qte'] * df['p_achat']
            df['Total Vente'] = df['qte'] * df['p_vente']
            df['Bénéfice'] = df['Total Vente'] - df['Total Achat']
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Capital Investi", f"{df['Total Achat'].sum():,.0f} CFA")
            c2.metric("Chiffre d'Affaires", f"{df['Total Vente'].sum():,.0f} CFA")
            c3.metric("Bénéfice Net", f"{df['Bénéfice'].sum():,.0f} CFA")
            
            st.write("### Inventaire détaillé")
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Le stock est vide. Allez dans 'Ajouter Stock' pour commencer.")

    elif choix == "Parts Associés":
        st.subheader("👥 Répartition des Bénéfices (20% / 40% / 40%)")
        df = pd.read_sql_query("SELECT * FROM stock", conn)
        if not df.empty:
            total_benef = (df['qte'] * (df['p_vente'] - df['p_achat'])).sum()
            st.info(f"Bénéfice total à partager : *{total_benef:,.0f} CFA*")
            
            col1, col2, col3 = st.columns(3)
            col1.warning(f"*Associé 1 (20%)*\n\n{total_benef * PART_1:,.0f} CFA")
            col2.success(f"*Associé 2 (40%)*\n\n{total_benef * PART_2:,.0f} CFA")
            col3.success(f"*Associé 3 (40%)*\n\n{total_benef * PART_3:,.0f} CFA")
        else:
            st.warning("Aucun bénéfice à calculer pour le moment.")
