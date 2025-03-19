#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import numpy as np

# -------------------------------------------------
# Initialisation des données en session
# -------------------------------------------------
if "catalog_costs" not in st.session_state:
    st.session_state.catalog_costs = []  # Catalogue des coûts (Nom, Prix)
if "catalog_services" not in st.session_state:
    st.session_state.catalog_services = []  # Catalogue des prestations (Nom, Prix)
if "log_costs" not in st.session_state:
    st.session_state.log_costs = []  # Historique des coûts (Nom, Prix, Date)
if "log_services" not in st.session_state:
    st.session_state.log_services = []  # Historique des prestations (Nom, Prix, Date)

st.title("Ninailz")

# -------------------------------------------------
# Création des onglets
# -------------------------------------------------
tab_add, tab_modify_catalog, tab_modify_logs, tab_datavis = st.tabs(
    ["Ajouter", "Modifier le catalogue", "Modifier l'historique", "Datavis"]
)

# -------------------------------------------------
# Onglet 1 : Ajouter des transactions
# -------------------------------------------------
with tab_add:
    st.header("Enregistrer une transaction")
    option = st.radio("Choisis :", ("Enregistrer un coût", "Enregistrer une prestation"))
    
    if option == "Enregistrer un coût":
        st.subheader("Ajouter un coût")
        # Filtrer les coûts valides (doivent avoir un nom)
        valid_costs = [item for item in st.session_state.catalog_costs if item.get("Nom")]
        if valid_costs:
            cost_names = [item["Nom"] for item in valid_costs]
            selected_cost = st.selectbox("Sélectionner un coût", cost_names)
            matching_item = next((item for item in valid_costs if item["Nom"] == selected_cost), None)
            # Forcer le prix à 0 si le champ est vide
            default_price = matching_item["Prix"] if matching_item and matching_item.get("Prix") is not None else 0.0
            price = st.number_input("Prix (€)", min_value=0.0, step=0.1, value=float(default_price))
            date_added = st.date_input("Date d'ajout", value=datetime.date.today())
            if st.button("Ajouter le coût", key="add_cost"):
                st.session_state.log_costs.append({
                    "Nom": selected_cost,
                    "Prix": price,
                    "Date": str(date_added)
                })
                st.success("Coût enregistré avec succès !")
                try:
                    st.experimental_rerun()  # Actualise l'interface
                except AttributeError:
                    pass
        else:
            st.info("Veuillez d'abord remplir le catalogue des coûts dans l'onglet 'Modifier le catalogue'.")
        
        st.subheader("Historique des coûts (lecture seule)")
        if st.session_state.log_costs:
            st.table(st.session_state.log_costs)
        else:
            st.info("Aucun coût enregistré pour l'instant.")
            
    else:  # Enregistrer une prestation
        st.subheader("Ajouter une prestation")
        valid_services = [item for item in st.session_state.catalog_services if item.get("Nom")]
        if valid_services:
            service_names = [item["Nom"] for item in valid_services]
            selected_service = st.selectbox("Sélectionner une prestation", service_names)
            matching_item = next((item for item in valid_services if item["Nom"] == selected_service), None)
            default_price = matching_item["Prix"] if matching_item and matching_item.get("Prix") is not None else 0.0
            price = st.number_input("Prix (€)", min_value=0.0, step=0.1, value=float(default_price))
            date_added = st.date_input("Date d'ajout", value=datetime.date.today(), key="date_service")
            if st.button("Ajouter la prestation", key="add_service"):
                st.session_state.log_services.append({
                    "Nom": selected_service,
                    "Prix": price,
                    "Date": str(date_added)
                })
                st.success("Prestation enregistrée avec succès !")
                try:
                    st.experimental_rerun()  # Actualise l'interface
                except AttributeError:
                    pass
        else:
            st.info("Veuillez d'abord remplir le catalogue des prestations dans l'onglet 'Modifier le catalogue'.")
        
        st.subheader("Historique des prestations (lecture seule)")
        if st.session_state.log_services:
            st.table(st.session_state.log_services)
        else:
            st.info("Aucune prestation enregistrée pour l'instant.")

# -------------------------------------------------
# Onglet 2 : Modifier le catalogue (nom / prix)
# -------------------------------------------------
with tab_modify_catalog:
    st.header("Modifier le catalogue de référence")
    
    st.subheader("Catalogue des coûts")
    df_catalog_costs = pd.DataFrame(st.session_state.catalog_costs, columns=["Nom", "Prix"])
    edited_df_catalog_costs = st.data_editor(df_catalog_costs, num_rows="dynamic", key="edit_catalog_costs")
    st.session_state.catalog_costs = edited_df_catalog_costs.to_dict("records")
    
    st.subheader("Catalogue des prestations")
    df_catalog_services = pd.DataFrame(st.session_state.catalog_services, columns=["Nom", "Prix"])
    edited_df_catalog_services = st.data_editor(df_catalog_services, num_rows="dynamic", key="edit_catalog_services")
    st.session_state.catalog_services = edited_df_catalog_services.to_dict("records")

# -------------------------------------------------
# Onglet 3 : Modifier l'historique (transactions)
# -------------------------------------------------
with tab_modify_logs:
    st.header("Modifier l'historique des transactions")
    
    st.subheader("Historique des coûts")
    df_log_costs = pd.DataFrame(st.session_state.log_costs, columns=["Nom", "Prix", "Date"])
    edited_df_log_costs = st.data_editor(df_log_costs, num_rows="dynamic", key="edit_log_costs")
    st.session_state.log_costs = edited_df_log_costs.to_dict("records")
    
    st.subheader("Historique des prestations")
    df_log_services = pd.DataFrame(st.session_state.log_services, columns=["Nom", "Prix", "Date"])
    edited_df_log_services = st.data_editor(df_log_services, num_rows="dynamic", key="edit_log_services")
    st.session_state.log_services = edited_df_log_services.to_dict("records")

# -------------------------------------------------
# Onglet 4 : Datavis (agrégation et visualisation)
# -------------------------------------------------
with tab_datavis:
    st.header("Data Visualisation")
    
    if st.session_state.log_costs or st.session_state.log_services:
        # Préparation des données mensuelles pour les coûts
        if st.session_state.log_costs:
            df_costs = pd.DataFrame(st.session_state.log_costs)
            df_costs['Date'] = pd.to_datetime(df_costs['Date'])
            df_costs['Mois'] = df_costs['Date'].dt.to_period('M').astype(str)
            monthly_costs = df_costs.groupby('Mois')['Prix'].sum().reset_index()
        else:
            monthly_costs = pd.DataFrame(columns=['Mois', 'Prix'])
        
        # Préparation des données mensuelles pour les prestations
        if st.session_state.log_services:
            df_services = pd.DataFrame(st.session_state.log_services)
            df_services['Date'] = pd.to_datetime(df_services['Date'])
            df_services['Mois'] = df_services['Date'].dt.to_period('M').astype(str)
            monthly_services = df_services.groupby('Mois')['Prix'].sum().reset_index()
        else:
            monthly_services = pd.DataFrame(columns=['Mois', 'Prix'])
        
        # Fusion sur la colonne 'Mois'
        df_merged = pd.merge(
            monthly_services, monthly_costs, on='Mois', how='outer', suffixes=('_services', '_costs')
        ).fillna(0)
        df_merged['Bénéfice'] = df_merged['Prix_services'] - df_merged['Prix_costs']
        df_merged = df_merged.sort_values('Mois')
        
        st.subheader("Données mensuelles")
        st.table(df_merged)
        
        # Diagramme en barres groupées
        x = np.arange(len(df_merged['Mois']))
        width = 0.25
        
        fig, ax = plt.subplots()
        ax.bar(x - width, df_merged['Prix_costs'], width, label="Dépenses")
        ax.bar(x, df_merged['Prix_services'], width, label="Rentrées")
        ax.bar(x + width, df_merged['Bénéfice'], width, label="Bénéfice")
        
        ax.set_xticks(x)
        ax.set_xticklabels(df_merged['Mois'])
        ax.set_xlabel("Mois")
        ax.set_ylabel("Montant (€)")
        ax.set_title("Bilan mensuel")
        plt.xticks(rotation=45)
        ax.legend()
        
        st.pyplot(fig)
    else:
        st.info("Aucune donnée pour la visualisation. Ajoutez d'abord des transactions.")





# In[ ]:




