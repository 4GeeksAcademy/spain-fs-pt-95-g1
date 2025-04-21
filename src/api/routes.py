from flask import Flask, request, jsonify, url_for, Blueprint
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy import func
from api.models import db, User, Anime, Favorites, On_Air, Genre
from api.utils import generate_sitemap, APIException
import requests
import time
import json
import bcrypt

api = Blueprint('api', __name__)
# Permite todas las origenes en desarrollo
# La configuración de CORS se realizará en app.py



def wait_for_rate_limit():
    time.sleep(1)  # Wait 1 second between requests

# endpoint para almacenar datos de api externa
# anime


@api.route('/anime', methods=['GET'])
def get_animes():
    animes = Anime.query.all()
    return jsonify([anime.serialize() for anime in animes]), 200


@api.route('/anime/sync/top', methods=['POST'])
def sync_anime():
    anime_api = 'https://api.jikan.moe/v4/anime'
    try:
        page = 1
        max_page = 50
        
        while page <= max_page:
            print(f"Sincronizando página {page}...")  
            response = requests.get(anime_api, params={'page': page})
            if response.status_code != 200:
                print(f"Error al obtener la página {page}: {response.status_code}")
                break

            anime_list = response.json().get('data', [])
            print(f"Número de animes en la página {page}: {len(anime_list)}")  
            for anime in anime_list:
                if anime.get('score') and anime['score'] >= 7:
                    exists = Anime.query.filter_by(
                        mal_id=anime['mal_id']).first()
                    trailer_data = anime.get('trailer')
                    trailer_url = trailer_data.get('url') if trailer_data else None
                    if not exists:
                        genre_names = [g['name']
                                       for g in anime.get('genres', [])]
                        genre_objs = []
                        for name in genre_names:
                            genre = Genre.query.filter_by(name=name).first()
                            if not genre:
                                genre = Genre(name=name)
                                db.session.add(genre)
                            genre_objs.append(genre)

                        new_anime = Anime(
                            mal_id=anime['mal_id'],
                            title=anime['title'],
                            synopsis=anime.get('synopsis'),
                            image_url=anime['images']['jpg']['image_url'],
                            episodes=anime.get('episodes'),
                            score=anime['score'],
                            airing=anime.get('airing', False),
                            genres=genre_objs,
                            trailer_url=trailer_url
                        )
                        db.session.add(new_anime)
            page += 1
            time.sleep(1)

            print(f"{page}")

        db.session.commit() 
        return jsonify({"message": "animes sincronizados"}), 200

    except Exception as e:
        db.session.rollback()
        print(f"Error durante la sincronización: {str(e)}") 
        return jsonify({"error": str(e)}), 500
 

@api.route('/anime/<int:anime_id>/recommendations/genres', methods=['GET'])
def get_genre_recommendations_by_anime_id(anime_id):
    anime = Anime.query.get(anime_id)
    if not anime:
        return jsonify({"message": "Anime not found"}), 404

    genres = anime.genres  # Obtener los géneros del anime actual
    if not genres:
        return jsonify({"recommendations": []}), 200

    genre_ids = [genre.id for genre in genres]

    # Buscar animes que compartan al menos un género y no sean el anime actual
    recommended_animes = (
        db.session.query(Anime)
        .join(Anime.genres)
        .filter(Genre.id.in_(genre_ids), Anime.id != anime_id)
        .group_by(Anime.id)
        .order_by(func.count(Anime.id).desc())
        .limit(5)
        .all()
    )

    serialized_recommendations = [rec.serialize() for rec in recommended_animes]
    return jsonify({"recommendations": serialized_recommendations}), 200


# Get anime by id - for individual page and searchbar

@api.route('/anime/<int:id>', methods=['GET'])
def get_animeId(id):
    anime = Anime.query.get(id)
    if not anime:
        return jsonify({"error": "Anime no disponible"}), 404
    return jsonify(anime.serialize()), 200


@api.route('/anime/on-air', methods=['POST'])
def get_on_air_anime():
    try:
        api_url = 'https://api.jikan.moe/v4/seasons/now'
        response = requests.get(api_url)
        season_now = response.json()

        for data in season_now['data']:
            check_exist = On_Air.query.filter_by(mal_id=data['mal_id']).first()
            if not check_exist:
                genre_names = [genre['name']
                               for genre in data.get('genres', [])]

                genre_objs = []
                for name in genre_names:
                    genre = Genre.query.filter_by(name=name).first()
                    if not genre:
                        genre = Genre(name=name)
                        db.session.add(genre)
                    genre_objs.append(genre)

                new_on_air = On_Air(
                    mal_id=data['mal_id'],
                    title=data['title'],
                    synopsis=data.get('synopsis'),
                    image_url=data['images']['jpg']['image_url'],
                    score=data.get('score'),
                    airing=data.get('airing', False),
                    genres=genre_objs  
                )
                db.session.add(new_on_air)

        db.session.commit()
        return jsonify({"message": "perfecto"}), 200

    except Exception as er:
        db.session.rollback()
        return jsonify({'error': f'ha habido un error: {str(er)}'}), 500


@api.route('/anime/on-air/list', methods=['GET'])
def get_on_air_list():
    on_air_animes = On_Air.query.all()
    return jsonify([anime.serialize() for anime in on_air_animes]), 200

# favorites


@api.route('/favorites', methods=['GET'])
def get_favorites():
    favorites = Favorites.query.all()
    return jsonify([favorite.serialize() for favorite in favorites]), 200


@api.route('/favorites', methods=['POST'])
def add_favorite():
    data = request.json
    favorite = Favorites(
        user_id=data['user_id'],
        anime_id=data['anime_id']
    )
    db.session.add(favorite)
    db.session.commit()
    return jsonify({"message": "Favorite added successfully"}), 200


@api.route('/favorites/<int:favorite_id>', methods=['DELETE'])
def delete_favorite(favorite_id):
    favorite = Favorites.query.get(favorite_id)
    if not favorite:
        return jsonify({"message": "Favorite not found"}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"message": "Favorite deleted successfully"}), 200

# ESTA PARTE CORRESPONDE A LA PARTE DE LOGIN, SIGNUP Y TOKEN.


@api.route('/signup', methods=['POST'])
def register_user():
    data = request.get_json()
    if data is None:
        return jsonify({"message": "Email and password are required"}), 400
    email = data['email']
    password = data['password']
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "User already exists"}), 400
    # Convertimos la contraseña en un array de bytes.
    bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()  # Generamos la sal
    # Sacamos la contraseña ya hasheada.
    hashed_password = bcrypt.hashpw(bytes, salt)
    new_user = User(  # Creamos al nuevo usuario con su email y la contraseña hasheada.
        email=email,
        # Era esto o guardarlo en el modelo como bytes, pero así es mas fácil de leer.
        password=hashed_password.decode('utf-8'),
        is_active=True
    )
    # Se prepara para añadir el nuevo usuario a la base de datos.
    db.session.add(new_user)
    db.session.commit()  # Se añade al usuario a la base de datos.
    return jsonify({"message": "User created successfully"}), 201


@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"message": "Email and password are required"}), 400
    email = data['email']
    password = data['password']
    user = User.query.filter_by(email=email).first()
    # Esto compara la contraseña introducida con la del usuario
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        return jsonify({"message": "Invalid user or password"}), 401
    # Aquí se crea el token.
    access_token = create_access_token(identity=user.id)
    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user_id": user.id
    }), 200


@api.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    return jsonify(user.serialize()), 200
