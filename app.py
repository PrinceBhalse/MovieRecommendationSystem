import streamlit as st
import pickle
import pandas as pd
import requests
import os
from dotenv import load_dotenv

# ------------------ File Downloader ------------------ #
def download_file(url, filename):
    if not os.path.exists(filename):
        try:
            st.write(f"Downloading {filename}...")
            response = requests.get(url)
            with open(filename, 'wb') as f:
                f.write(response.content)
            st.write(f"{filename} downloaded successfully.")
        except Exception as e:
            st.error(f"Failed to download {filename}: {e}")

# ------------------ File URLs ------------------ #
similarity_url = "https://huggingface.co/spaces/Princebhalse92/movie-model-files/resolve/main/similarity.pkl"
movie_dict_url = "https://huggingface.co/spaces/Princebhalse92/movie-model-files/resolve/main/movie_dict.pkl"

download_file(movie_dict_url, "movie_dict.pkl")
download_file(similarity_url, "similarity.pkl")

# ------------------ Load Data ------------------ #
try:
    with open('movie_dict.pkl', 'rb') as f:
        movies_dict = pickle.load(f)
    movies = pd.DataFrame(movies_dict)
except Exception as e:
    st.error(f"Error loading movie_dict.pkl: {e}")
    st.stop()

try:
    with open('similarity.pkl', 'rb') as f:
        similarity = pickle.load(f)
except Exception as e:
    st.error(f"Error loading similarity.pkl: {e}")
    st.stop()

# ------------------ TMDB API Setup ------------------ #
load_dotenv()
api_key = os.getenv('TMDB_API_KEY')
if not api_key:
    st.error("TMDB API key not found! Please set it in your environment.")
    st.stop()

# ------------------ Poster Fetcher ------------------ #
def fetch_poster(movie_id):
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}'
    response = requests.get(url)
    data = response.json()
    return "https://image.tmdb.org/t/p/w500/" + data.get('poster_path', '')

# ------------------ Recommendation Logic ------------------ #
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies_posters.append(fetch_poster(movie_id))
        recommended_movies.append(movies.iloc[i[0]].title)

    return recommended_movies, recommended_movies_posters

# ------------------ Streamlit UI ------------------ #
st.title('🎬 Movie Recommendation System')

select_movie_name = st.selectbox('What type of movies do you want?', movies['title'].values)

if st.button('Recommend'):
    names, posters = recommend(select_movie_name)
    cols = st.columns(5)
    for i in range(len(names)):
        with cols[i]:
            st.text(names[i])
            st.image(posters[i])
