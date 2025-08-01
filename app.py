import streamlit as st
import pickle
import pandas as pd
import requests
import os
from dotenv import load_dotenv

with open('movie_dict.pkl', 'rb') as f:
    movies_dict = pickle.load(f)

movies = pd.DataFrame(movies_dict)

with open('similarity.pkl', 'rb') as f:
    similarity = pickle.load(f)

# Get the API key
load_dotenv()
api_key = st.secrets["TMDB"]["TMDB_API_KEY"]


def fetch_poster(movie_id):
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}'
    response = requests.get(url)
    data = response.json()
    print(data)

    return "https://image.tmdb.org/t/p/w500/" + data['poster_path']


def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    for i in movies_list:
        print(i[0])
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies_posters.append(fetch_poster(movie_id))
        recommended_movies.append(movies.iloc[i[0]].title)

    return recommended_movies, recommended_movies_posters


st.title('Movie Recommendation System')

select_movie_name = st.selectbox('What type of movies you want: ', movies['title'].values)

if st.button('recommend'):
    names, posters = recommend(select_movie_name)

    cols = st.columns(5)

    for i in range(len(names)):
        with cols[i]:
            st.text(names[i])
            st.image(posters[i])
