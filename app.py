import streamlit as st
import pickle
import pandas as pd
import requests
import time

st.set_page_config(page_title="Flixora", layout="wide")

st.markdown("""
<style>
body {
    background-color: #000000;
    background-image: url('https://assets.foho.ai/wallpapers/965f2970-703c-4a7b-bf6d-23b25e6afa5f.webp');
    background-size: cover;
    background-attachment: fixed;
    font-family: 'Poppins', sans-serif;
}

.stApp {
    background: rgba(0,0,0,0.92);
}

h1 {
    text-align: center;
    font-size: 42px;
    background: linear-gradient(90deg, #FFD700, #fff8dc, #FFD700);
    background-size: 200% auto;
    color: transparent;
    background-clip: text;
    -webkit-background-clip: text;
    animation: shimmer 3s linear infinite;
}

.movie-card {
    background: rgba(10,10,10,0.95);
    padding: 15px;
    border-radius: 18px;
    text-align: center;
    margin-bottom: 20px;
    border: 2px solid transparent;
    background-image:
        linear-gradient(rgba(10,10,10,0.95), rgba(10,10,10,0.95)),
        linear-gradient(270deg, #FFD700, #ffcc00, #FFD700);
    background-origin: border-box;
    background-clip: padding-box, border-box;
    background-size: 100% 100%, 300% 300%;
    animation: borderMove 4s linear infinite;
    transition: 0.4s ease;
}

.movie-card:hover {
    transform: translateY(-10px) scale(1.05);
    box-shadow: 0 0 30px rgba(255,215,0,0.8);
}

.movie-title {
    margin-top: 12px;
    font-weight: bold;
    font-size: 18px;
    background: linear-gradient(90deg, #FFD700, #fff8dc, #FFD700);
    background-size: 200% auto;
    color: transparent;
    background-clip: text;
    -webkit-background-clip: text;
    animation: shimmer 4s linear infinite;
}

.stButton button {
    background: linear-gradient(90deg, #FFD700, #ffcc00);
    color: black !important;
    border-radius: 30px;
    padding: 12px 30px;
    font-weight: bold;
    transition: 0.4s ease;
    box-shadow: 0 0 20px rgba(255,215,0,0.6);
}

.stButton button:hover {
    background: black !important;
    color: #FFD700 !important;
    border: 1px solid #FFD700;
    transform: scale(1.1);
    box-shadow: 0 0 40px rgba(255,215,0,1);
}

[data-testid="column"] {
    overflow: visible !important;
}

@keyframes shimmer {
    0% { background-position: 0% center; }
    100% { background-position: 200% center; }
}

@keyframes borderMove {
    0% { background-position: 0% 50%; }
    100% { background-position: 200% 50%; }
}
</style>
""", unsafe_allow_html=True)

movies = pickle.load(open('movies.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

API_KEY = st.secrets["TMDB_API"]
    
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return "https://via.placeholder.com/300x450/000000/FFD700?text=No+Image"
        data = response.json()
        poster_path = data.get("poster_path")
        if poster_path:
            return "https://image.tmdb.org/t/p/w500/" + poster_path
        return "https://via.placeholder.com/300x450/000000/FFD700?text=No+Image"
    except:
        return "https://via.placeholder.com/300x450/000000/FFD700?text=No+Image"

def fetch_trailer(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={API_KEY}&language=en-US"
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return None
        data = response.json()
        results = data.get("results", [])
        for video in results:
            if video.get("type") == "Trailer" and video.get("site") == "YouTube":
                return f"https://www.youtube.com/watch?v={video.get('key')}"
        return None
    except:
        return None

def recommend(movie):
    movie_row = movies[movies["title"] == movie]
    if movie_row.empty:
        return [], [], []
    
    movie_index = movie_row.index[0]
    distances = similarity[movie_index]
    movies_list = sorted(
        list(enumerate(distances)),
        key=lambda x: x[1],
        reverse=True
    )[1:6]

    recommended_movies = []
    recommended_posters = []
    recommended_trailers = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))
        recommended_trailers.append(fetch_trailer(movie_id))

    return recommended_movies, recommended_posters, recommended_trailers

st.markdown("<h1>🎬 Flixora</h1>", unsafe_allow_html=True)

selected_movie_name = st.selectbox("Select a movie", movies["title"].values)

if st.button("Recommend"):
    with st.spinner("Finding the best movies for you... 🍿"):
        names, posters, trailers = recommend(selected_movie_name)

    if not names:
        st.error("Movie not found.")
    else:
        cols = st.columns(5)

        for i, col in enumerate(cols):
            with col:
                time.sleep(0.2)
                st.markdown("<div class='movie-card'>", unsafe_allow_html=True)
                st.markdown(f"""
                <div style="overflow:hidden; border-radius:15px;">
                    <img src="{posters[i]}" style="width:100%; transition:0.4s;"
                    onmouseover="this.style.transform='scale(1.1)'"
                    onmouseout="this.style.transform='scale(1)'"/>
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"<div class='movie-title'>{names[i]}</div>", unsafe_allow_html=True)
                if trailers[i]:
                    st.video(trailers[i])
                else:
                    st.write("Trailer not available")
                st.markdown("</div>", unsafe_allow_html=True)
