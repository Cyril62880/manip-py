import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns

# 🔧 Configuration de la page - doit être le premier appel Streamlit
st.set_page_config(page_title="Recettes Gourmandes", layout="wide")

# Chargement des données
@st.cache_data
def load_data():
    df = pd.read_csv("clean_recipes.csv")
    # Dérivation de nouvelles colonnes
    df = df.assign(complexity_normalized=df['complexity'].map(lambda x: 'Simple' if x == 'Easy' else 'Complex'))
    return df

df = load_data()

# Sidebar - Navigation
st.sidebar.title("🍽️ Menu")
page = st.sidebar.radio("Aller à :", ["Accueil", "Statistiques"])

# Fonction pour afficher une recette complète
def show_recipe(recipe):
    st.markdown(f"## {recipe['title']}")

    # Image locale
    image_path = f"images/{recipe['image']}.jpg"
    if os.path.exists(image_path):
        st.image(image_path, use_container_width=True)

    st.markdown(f"**Complexité** : {recipe['complexity']}")
    st.markdown(f"**Nombre d'ingrédients** : {recipe['num_ingredients']}")

    # Affichage des ingrédients sous forme de liste à puces
    st.markdown("### Ingrédients :")
    ingredients = recipe['ingredients_text'].split(', ')
    for ingredient in ingredients:
        st.markdown(f"- {ingredient}")

    # Affichage des instructions sous forme de liste numérotée
    st.markdown("### Instructions :")
    instructions = recipe['instructions'].split('. ')
    for i, instruction in enumerate(instructions, start=1):
        st.markdown(f"{i}. {instruction.strip()}")

    # Suggestions en bas
    st.markdown("---")
    st.markdown("### Recettes Similaires")
    same_complexity = df[df["complexity"] == recipe["complexity"]].sample(3)
    for _, r in same_complexity.iterrows():
        if r["id"] != recipe["id"]:
            st.markdown(f"👉 [{r['title']}]('?id={r['id']}')")

# Vérification des paramètres de l'URL
params = st.query_params
if "id" in params:
    try:
        rec_id = int(params["id"][0])
        recipe = df[df["id"] == rec_id].iloc[0]
        show_recipe(recipe)
    except:
        st.error("Recette introuvable.")
else:
    # Page Accueil
    if page == "Accueil":
        st.title("Bienvenue sur Recettes Gourmandes 👩‍🍳")
        st.markdown("Explorez notre collection de recettes savoureuses. Utilisez la barre de recherche ci-dessous pour trouver une recette.")

        # Barre de recherche
        query = st.text_input("🔍 Rechercher une recette ou un ingrédient")

        # Filtrer les recettes en fonction de la recherche
        if query:
            query_lower = query.lower()
            filtered_df = df[df["title"].str.contains(query_lower, case=False, na=False) |
                             df["ingredients_text"].str.contains(query_lower, case=False, na=False)]
        else:
            filtered_df = df

        # Pagination
        page_size = 10
        num_pages = (len(filtered_df) + page_size - 1) // page_size  # Calculer le nombre total de pages
        current_page = st.number_input("Page", min_value=1, max_value=num_pages, value=1, step=1)

        start_idx = (current_page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_df = filtered_df.iloc[start_idx:end_idx]

        # Affichage des recettes paginées
        if not paginated_df.empty:
            for _, recipe in paginated_df.iterrows():
                st.markdown(f"#### [{recipe['title']}]('?id={recipe['id']}')")
                st.markdown(f"- **Complexité** : {recipe['complexity']}")
                st.markdown(f"- **Nombre d'ingrédients** : {recipe['num_ingredients']}")
                st.markdown("---")
        else:
            st.markdown("Aucune recette trouvée.")

        # Quelques stats
        st.markdown("### Statistiques :")
        col1, col2, col3 = st.columns(3)
        col1.metric("Nombre total de recettes", len(df))
        col2.metric("Ingrédients uniques", df['ingredients_text'].str.split(', ').explode().nunique())
        col3.metric("Recette la plus complexe", df.sort_values("num_ingredients", ascending=False).iloc[0]["title"])

    # Page Statistiques
    elif page == "Statistiques":
        st.title("Statistiques des Recettes")

        # Graphique 1 : Nombre de recettes par complexité
        st.subheader("Nombre de recettes par complexité")
        complexity_counts = df['complexity'].value_counts()
        plt.figure(figsize=(10, 6))
        sns.barplot(x=complexity_counts.index, y=complexity_counts.values, palette='viridis')
        plt.title('Nombre de recettes par complexité')
        plt.xlabel('Complexité')
        plt.ylabel('Nombre de recettes')
        st.pyplot(plt)

        # Graphique 2 : Nombre total d'ingrédients par complexité
        st.subheader("Nombre total d'ingrédients par complexité")
        total_ingredients_by_complexity = df.groupby('complexity')['num_ingredients'].sum()
        plt.figure(figsize=(10, 6))
        sns.barplot(x=total_ingredients_by_complexity.index, y=total_ingredients_by_complexity.values, palette='viridis')
        plt.title('Nombre total d\'ingrédients par complexité')
        plt.xlabel('Complexité')
        plt.ylabel('Nombre total d\'ingrédients')
        st.pyplot(plt)

        # Graphique 3 : Distribution de la complexité normalisée
        st.subheader("Distribution de la complexité normalisée")
        plt.figure(figsize=(10, 6))
        sns.countplot(data=df, x='complexity_normalized', palette='viridis')
        plt.title('Distribution de la complexité normalisée')
        plt.xlabel('Complexité normalisée')
        plt.ylabel('Nombre de recettes')
        st.pyplot(plt)
