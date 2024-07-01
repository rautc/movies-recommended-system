import streamlit as st
import pickle
import pandas as pd
import requests

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=5570249a924c08ddeafbbdac4358a6a4&language=en-US".format(movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path

def fetch_movie_details(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=5570249a924c08ddeafbbdac4358a6a4&language=en-US".format(movie_id)
    data = requests.get(url)
    data = data.json()
    return data

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    recommended_movie_ids = []

    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)
        recommended_movie_ids.append(movie_id)

    return recommended_movie_names, recommended_movie_posters, recommended_movie_ids

# Load the movies and similarity data
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

st.header('Movie Recommender System')

movie_list = movies['title'].values
selected_movie_name = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

if st.button('Show Recommendation'):
    recommended_movie_names, recommended_movie_posters, recommended_movie_ids = recommend(selected_movie_name)
    for i in range(5):
        col = st.columns(1)[0]
        with col:
            st.image(recommended_movie_posters[i])
            st.write(recommended_movie_names[i])
            if st.button(f'More Info - {recommended_movie_names[i]}', key=f'more_info_{i}'):
                    st.session_state['movie_id'] = recommended_movie_ids[i]
                    st.session_state['movie_name'] = recommended_movie_names[i]
                    st.experimental_rerun()


if 'movie_id' in st.session_state:

    movie_id = st.session_state['movie_id']
    movie_name = st.session_state['movie_name']
    movie_details = fetch_movie_details(movie_id)
    st.write(f"**Title:** {movie_details['title']}")
    st.write(f"**Release Date:** {movie_details['release_date']}")
    st.write(f"**Overview:** {movie_details['overview']}")
    st.write(f"**Genre:** {', '.join([genre['name'] for genre in movie_details['genres']])}")

    if 'credits' in movie_details:
        st.write(f"**Cast:**")
        for cast in movie_details['credits']['cast'][:5]:
            st.write(f"  - {cast['name']} as {cast['character']}")
        st.write(f"**Crew:**")
        for crew in movie_details['credits']['crew'][:5]:
            st.write(f"  - {crew['name']} as {crew['job']}")

