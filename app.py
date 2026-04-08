[22:22, 08/04/2026] Halving 05: import streamlit as st
import pandas as pd
import os

# Nom du fichier qui sert de base de données permanente
DB_FILE = "save_stock.csv"

st.set_page_config(page_title="Elec Master Tech", page_icon="⚡")
st.title("⚡ Logiciel de Gestion Elec Master Tech")

# Fonction pour charger les données sauvegardées sur GitHub
def charger_donnees():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Article", "Prix", "Quantité"])

# --- PARTIE 1 : ENREGISTREMENT ---
with st.expander("📝 Enregistrer un nouvel Article ou Service"):
    nom = st.text_input("Nom de l'article (ex: Câble, Ampoule, Main d'oeuvre)")
    prix = st.number_input("Prix (en FCFA)", min_value=0, step=50)
    quantite = st.number_input("Quantité", min_value=1, step=1)
    
    if st.button("Valider l'enregistrement"):
        if nom:
            df = charger_donnees()
            nouvelle_ligne = pd.DataFrame({"Article": [nom], "Prix": [prix], "Quantité": [quantite]})
            df = pd.concat([df, nouvelle_ligne], ignore_index=True)
            
            # Sauvegarde dans le fichier permanent
            df.to_csv(DB_FILE, index=False)
            st.success(f"✅ {nom} enregistré avec succès !")
            st.rerun()
        else:
            st.error("Veuillez entrer un nom.")

# --- PARTIE 2 : CONSULTATION DU STOCK ---
st.subheader("📋 État de votre Stock / Ventes")
donnees = charger_donnees()

if not donnees.empty:
    st.dataframe(donnees, use_container_width=True)
    
    # Calcul automatique du total pour ton bilan
    total = (donnees['Prix'] * donnees['Quantité']).sum()
    st.info(f"💰 Valeur totale dans le registre : {total} FCFA")
else:
    st.write("Le registre est vide.")

# Bouton de sécurité dans la barre latérale
if st.sidebar.button("⚠️ Effacer tout le registre"):
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        st.sidebar.success("Registre vidé.")
        st.rerun()
[23:55, 08/04/2026] Halving 05: import streamlit as st
import sqlite3
import pandas as pd

# --- CONFIGURATION ---
PART_ASSOCIE_1 = 0.40  # 40% par exemple
PART_ASSOCIE_2 = 0.30  # 30%
PART_ASSOCIE_3 = 0.30  # 30%

# --- BASE DE DONNÉES ---
def init_db():
    conn = sqlite3.connect('elec_master_pro.db')
    c = conn.cursor()
    # Table pour le stock et les ventes
    c.execute('''CREATE TABLE IF NOT EXISTS inventaire (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nom_article TEXT,
                    quantite INTEGER,
                    prix_achat REAL,
                    prix_vente REAL,
                    date_ajout TEXT)''')
    # Table pour les mouvements de caisse (Entrées/Sorties hors ventes)
    c.execute('''CREATE TABLE IF NOT EXISTS flux_caisse (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT,
                    motif TEXT,
                    montant REAL,
                    date TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- INTERFACE ---
st.set_page_config(page_title="Elec Master Pro", layout="wide")
st.title("🚀 Système de Gestion Elec Master Pro")

menu = ["Tableau de Bord", "Achat / Stock", "Ventes", "Parts Actionnaires", "Caisse"]
choix = st.sidebar.selectbox("Menu", menu)

# --- SECTION 1 : ACHAT ET STOCK ---
if choix == "Achat / Stock":
    st.subheader("📦 Enregistrer un nouvel achat de stock")
    with st.form("form_achat"):
        nom = st.text_input("Nom de l'article")
        qte = st.number_input("Nombre d'articles", min_value=1)
        p_achat = st.number_input("Prix d'achat Unitaire", min_value=0.0)
        p_vente = st.number_input("Prix de vente Unitaire prévu", min_value=0.0)
        btn = st.form_submit_button("Ajouter au stock")
        
        if btn:
            conn = sqlite3.connect('elec_master_pro.db')
            c = conn.cursor()
            c.execute("INSERT INTO inventaire (nom_article, quantite, prix_achat, prix_vente, date_ajout) VALUES (?,?,?,?,?)",
                      (nom, qte, p_achat, p_vente, pd.Timestamp.now()))
            conn.commit()
            st.success(f"{nom} ajouté au stock !")

# --- SECTION 2 : TABLEAU DE BORD (Bénéfices/Pertes) ---
elif choix == "Tableau de Bord":
    st.subheader("📊 Analyse des Bénéfices et Performance")
    conn = sqlite3.connect('elec_master_pro.db')
    df = pd.read_sql_query("SELECT * FROM inventaire", conn)
    
    if not df.empty:
        df['Investissement'] = df['quantite'] * df['prix_achat']
        df['CA_Prevu'] = df['quantite'] * df['prix_vente']
        df['Benefice_Prevu'] = df['CA_Prevu'] - df['Investissement']
        
        total_investi = df['Investissement'].sum()
        total_benefice = df['Benefice_Prevu'].sum()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Capital Investi", f"{total_investi} CFA")
        c2.metric("Bénéfice Global Prévu", f"{total_benefice} CFA")
        c3.metric("Articles en Stock", len(df))
        
        st.write("### Détails du Stock")
        st.dataframe(df)
    else:
        st.info("Le stock est vide.")

# --- SECTION 3 : PARTS ACTIONNAIRES ---
elif choix == "Parts Actionnaires":
    st.subheader("👥 Répartition des bénéfices")
    conn = sqlite3.connect('elec_master_pro.db')
    df = pd.read_sql_query("SELECT * FROM inventaire", conn)
    
    if not df.empty:
        benef_total = (df['quantite'] * df['prix_vente'] - df['quantite'] * df['prix_achat']).sum()
        st.write(f"*Bénéfice à partager : {benef_total} CFA*")
        
        col1, col2, col3 = st.columns(3)
        col1.info(f"Associer 1 (40%)\n\n*{benef_total * 0.4:.2f} CFA*")
        col2.info(f"Associer 2 (30%)\n\n*{benef_total * 0.3:.2f} CFA*")
        col3.info(f"Associer 3 (30%)\n\n*{benef_total * 0.3:.2f} CFA*")
    else:
        st.warning("Pas de données pour le calcul des parts.…
