import streamlit as st
import pickle 
import pandas as pd
import requests
import google.generativeai as genai 

genai.configure(api_key="Enter your API Key") 

popu_meh = pickle.load(open('popu.pkl','rb'))
popu_data = pd.DataFrame(popu_meh)

def popular(popu_data):
    popu_data_sorted = popu_data.sort_values(by="popularity", ascending=False)
    top_50_movies = popu_data_sorted.head(50)

    top_50 = []
    top_50_posters = []

    for index, row in top_50_movies.iterrows():
        movie_id = row['id']  # Assuming 'id' is the column name containing movie IDs
        top_50.append(row['title'])
        top_50_posters.append(fetch_poster(movie_id))

    st.title('Top 50 Popular Movies')
    num_cols = 3
    num_movies = len(top_50)
    num_rows = (num_movies + num_cols - 1) // num_cols  # Calculate number of rows needed

    cols = st.columns(num_cols)

    for i in range(num_rows):
        for j in range(num_cols):
            index = i * num_cols + j
            if index < num_movies:
                with cols[j]:
                    st.text(top_50[index])
                    if top_50_posters[index] is not None:
                        st.image(top_50_posters[index])
                    else:
                        st.write("Poster not available")



def fetch_poster(movie_id):
    response = requests.get('https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US'.format(movie_id))
    data = response.json()

    if data['poster_path'] is not None:
        return "https://image.tmdb.org/t/p/w500/" + data['poster_path']
    else:
        return None

def recommend(movie):
    if movie.lower() not in movies['title'].str.lower().tolist():
        st.write("Sorry we don't have this movie in our database")
        st.write("Here are some recommendations with AI")
        recommend_with_ai(movie)
    else:
        movie_index = movies[movies['title'].str.lower() == movie.lower()].index[0]
        distances = similarity[movie_index]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:51]

        recommended_movies = []
        recommended_movies_posters = []
        for i in movies_list:
            movie_id = movies.iloc[i[0]].movie_id
            recommended_movies.append(movies.iloc[i[0]].title)
            recommended_movies_posters.append(fetch_poster(movie_id))

        return recommended_movies, recommended_movies_posters


def recommend_with_ai(movie):
    generation_config = {"max_output_tokens": 2000}

    model = genai.GenerativeModel("gemini-pro", generation_config = generation_config)
    response = model.generate_content({f"Give me 20 movies similar to '{movie}' with their title and a short description:\n"})
    
    st.write(response.text)

movies_dict = pickle.load(open('movie_dict.pkl','rb'))
movies = pd.DataFrame(movies_dict)

similarity = pickle.load(open('similarity.pkl','rb'))

st.title(':rainbow[MovieMaven]')
st.subheader('Discover your next favorite film')


selected_movie_name = st.text_input('Enter a movie', '', autocomplete='on')


col1, col2 = st.columns(2)

with col1:
    b1 = st.button('Recommend')

if b1:
    names_posters = recommend(selected_movie_name)
    if names_posters:
        names, posters = names_posters
        num_cols = 3
        num_movies = len(names)
        num_rows = (num_movies + num_cols - 1) // num_cols  # Calculate number of rows needed

        cols = st.columns(num_cols)

        for i in range(num_rows):
            for j in range(num_cols):
                index = i * num_cols + j
                if index < num_movies:
                    with cols[j]:
                        st.text(names[index])
                        if posters[index] is not None:
                            st.image(posters[index])
                        else:
                            st.write("Poster not available")

    st.session_state['recommendations_requested'] = True

if 'recommendations_requested' not in st.session_state:
    popular(popu_data)
    st.session_state['recommendations_requested'] = False


