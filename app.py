import streamlit as st

# Configuration de la page
st.set_page_config(page_title="Elec Master Tech", page_icon="⚡")

st.title("⚡ Elec Master Tech")
st.write("Gestionnaire de vente professionnel")

# Boutons d'action
col1, col2 = st.columns(2)

with col1:
    if st.button("💰 ENCAISSER (Entrée)", type="primary"):
        st.success("Argent encaissé avec succès !")

with col2:
    if st.button("💸 DÉPENSER (Sortie)"):
        st.warning("Dépense enregistrée.")

st.divider()

# Section Bilan
st.subheader("📊 Bilan de l'entreprise")
c1, c2 = st.columns(2)
c1.metric(label="Ventes totales", value="500 000 FCFA")
c2.metric(label="Dépenses", value="120 000 FCFA")