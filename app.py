import streamlit as st
import pandas as pd
import sqlite3

# --- CONFIGURATION ---
MOT_DE_PASSE = "elec2026" 
PART_1, PART_2, PART_3 = 0.20, 0.40, 0.40

# --- BASE DE DONNÉES ---
def init_db():
    conn = sqlite3.connect('elec_master_v5.db', check_same_thread=False)
    c = conn.cursor()
    # On garde le stock acheté
    c.execute('''CREATE TABLE IF NOT EXISTS stock 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nom TEXT, qte_achat INTEGER, p_achat REAL, p_vente REAL)''')
    # On ajoute une table pour les ventes
    c.execute('''CREATE TABLE IF NOT EXISTS ventes 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, article_id INTEGER, qte_vendue INTEGER, date TEXT)''')
    conn.commit()
    return conn

conn = init_db()

# --- SÉCURITÉ ---
if 'authentifie' not in st.session_state:
    st.session_state['authentifie'] = False

if not st.session_state['authentifie']:
    st.title("🔐 Elec Master Tech")
    pwd = st.text_input("Code secret", type="password")
    if st.button("Se connecter"):
        if pwd == MOT_DE_PASSE:
            st.session_state['authentifie'] = True
            st.rerun()
        else: st.error("Code incorrect")
    st.stop()

# --- INTERFACE ---
st.set_page_config(page_title="Elec Master Tech Pro", layout="wide")
menu = ["📊 Tableau de Bord", "📦 Ajouter Stock", "💰 Enregistrer une Vente", "👥 Parts Associés"]
choix = st.sidebar.radio("Navigation", menu)

# --- 1. AJOUTER STOCK ---
if choix == "📦 Ajouter Stock":
    st.subheader("Enregistrer du nouveau matériel")
    with st.form("ajout"):
        nom = st.text_input("Nom de l'article")
        qte = st.number_input("Quantité achetée", min_value=1)
        pa = st.number_input("Prix d'achat unitaire (CFA)", min_value=0.0)
        pv = st.number_input("Prix de vente unitaire (CFA)", min_value=0.0)
        if st.form_submit_button("Ajouter au stock"):
            conn.execute("INSERT INTO stock (nom, qte_achat, p_achat, p_vente) VALUES (?,?,?,?)", (nom, qte, pa, pv))
            conn.commit()
            st.success(f"{nom} ajouté !")

# --- 2. VENDRE UN ARTICLE ---
elif choix == "💰 Enregistrer une Vente":
    st.subheader("Marquer un article comme vendu")
    df_stock = pd.read_sql_query("SELECT * FROM stock", conn)
    if not df_stock.empty:
        with st.form("vente"):
            article_nom = st.selectbox("Choisir l'article vendu", df_stock['nom'].tolist())
            qte_v = st.number_input("Quantité vendue", min_value=1)
            if st.form_submit_button("Valider la vente"):
                id_art = df_stock[df_stock['nom'] == article_nom]['id'].values[0]
                conn.execute("INSERT INTO ventes (article_id, qte_vendue) VALUES (?,?)", (int(id_art), qte_v))
                conn.commit()
                st.success(f"Vente de {qte_v} {article_nom} enregistrée !")
    else: st.info("Le stock est vide.")

# --- 3. TABLEAU DE BORD (AVEC RESTE) ---
elif choix == "📊 Tableau de Bord":
    st.subheader("État des Stocks et Finances")
    df_s = pd.read_sql_query("SELECT * FROM stock", conn)
    df_v = pd.read_sql_query("SELECT article_id, SUM(qte_vendue) as vendus FROM ventes GROUP BY article_id", conn)
    
    if not df_s.empty:
        df = pd.merge(df_s, df_v, left_on='id', right_on='article_id', how='left').fillna(0)
        df['Reste'] = df['qte_achat'] - df['vendus']
        df['Bénéfice Réalisé'] = df['vendus'] * (df['p_vente'] - df['p_achat'])
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Bénéfice Réel (Ventes)", f"{df['Bénéfice Réalisé'].sum():,.0f} CFA")
        c2.metric("Valeur du Stock Restant", f"{(df['Reste'] * df['p_vente']).sum():,.0f} CFA")
        
        st.write("### Inventaire des stocks")
        # Affichage avec des couleurs pour le reste
        st.dataframe(df[['nom', 'qte_achat', 'vendus', 'Reste', 'p_achat', 'p_vente']], use_container_width=True)
    else: st.info("Aucune donnée.")

# --- 4. PARTS ---
elif choix == "👥 Parts Associés":
    st.subheader("Répartition des Bénéfices sur les Ventes")
    df_s = pd.read_sql_query("SELECT * FROM stock", conn)
    df_v = pd.read_sql_query("SELECT article_id, SUM(qte_vendue) as vendus FROM ventes GROUP BY article_id", conn)
    if not df_s.empty and not df_v.empty:
        df = pd.merge(df_s, df_v, left_on='id', right_on='article_id', how='inner')
        total_benef = (df['vendus'] * (df['p_vente'] - df['p_achat'])).sum()
        st.write(f"Bénéfice total encaissé : *{total_benef:,.0f} CFA*")
        col1, col2, col3 = st.columns(3)
        col1.warning(f"Associé 1 (20%)\n\n{total_benef*0.2:,.0f}")
        col2.success(f"Associé 2 (40%)\n\n{total_benef*0.4:,.0f}")
        col3.success(f"Associé 3 (40%)\n\n{total_benef*0.4:,.0f}")
