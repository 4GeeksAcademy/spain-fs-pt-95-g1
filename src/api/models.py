from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Integer, Text, ForeignKey, Float, func, Table, Column, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

# Inicializar la DB
db = SQLAlchemy()

# MODELOS


class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)
    favorites: Mapped[List["Favorites"]] = relationship(back_populates="user")
    watching: Mapped[List["Watching"]] = relationship(back_populates="user")

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "favorites": [fav.anime.serialize() for fav in self.favorites],
            "watching": [watch.anime.serialize() for watch in self.watching],
        }


class UserPreference(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    genre: Mapped[str] = mapped_column(String(100))
    duration: Mapped[str] = mapped_column(String(100))
    theme: Mapped[str] = mapped_column(String(50))
    tone: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.current_timestamp())

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "genre": self.genre,
            "duration": self.duration,
            "theme": self.theme,
            "tone": self.tone,
            "created_at": self.created_at
        }


class Anime(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    mal_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    synopsis: Mapped[str] = mapped_column(Text, nullable=True)
    image_url: Mapped[str] = mapped_column(String(500), nullable=True)
    episodes: Mapped[int] = mapped_column(Integer, nullable=True)
    score: Mapped[float] = mapped_column(Float, nullable=True)
    airing: Mapped[bool] = mapped_column(Boolean, nullable=False)
    favorites: Mapped[List["Favorites"]] = relationship(back_populates="anime")
    watching: Mapped[List["Watching"]] = relationship(back_populates="anime")
    genres: Mapped[List["Genre"]] = relationship(secondary="anime_genre", back_populates="animes")
    trailer_url: Mapped[str] = mapped_column(String(500), nullable=True)
    def serialize(self):
        return {
            "id": self.id,
            "mal_id": self.mal_id,
            "title": self.title,
            "synopsis": self.synopsis,
            "image_url": self.image_url,
            "episodes": self.episodes,
            "score": self.score,
            "genres": [genre.serialize() for genre in self.genres],
            "airing": self.airing,
            "trailer": {"url": self.trailer_url} if self.trailer_url else None
        }


class On_Air(db.Model):
    __tablename__ = 'on_air'
    id: Mapped[int] = mapped_column(primary_key=True)
    mal_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    synopsis: Mapped[str] = mapped_column(Text, nullable=True)
    image_url: Mapped[str] = mapped_column(String(500), nullable=True)
    score: Mapped[float] = mapped_column(Float, nullable=True)
    airing: Mapped[bool] = mapped_column(Boolean, nullable=False)
    genres: Mapped[List["Genre"]] = relationship(secondary="onair_genre", back_populates="on_airs")

    def serialize(self):
        return {
            "id": self.id,
            "mal_id": self.mal_id,
            "title": self.title,
            "synopsis": self.synopsis,
            "image_url": self.image_url,
            "score": self.score,
            "genres": [genre.serialize() for genre in self.genres],
            "airing": self.airing
        }
    
class Genre(db.Model):
    __tablename__ = 'genre'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    animes: Mapped[List["Anime"]] = relationship(secondary="anime_genre", back_populates="genres")
    on_airs: Mapped[List["On_Air"]] = relationship(secondary="onair_genre", back_populates="genres")

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name
        }


class Favorites(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    anime_id: Mapped[int] = mapped_column(
        ForeignKey('anime.id'), nullable=False)
    user: Mapped["User"] = relationship(back_populates="favorites")
    anime: Mapped["Anime"] = relationship(back_populates="favorites")

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "anime_id": self.anime_id
        }


class Watching(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=False)
    anime_id: Mapped[int] = mapped_column(
        ForeignKey('anime.id'), nullable=False)
    user: Mapped["User"] = relationship(back_populates="watching")
    anime: Mapped["Anime"] = relationship(back_populates="watching")

    def serialize(self):
        return {
            "id": self.id,
            "anime_id": self.anime_id,
            "user_id": self.user_id
        }

# TABLAS INTERMEDIAS


anime_genre = Table(
    'anime_genre',
    db.metadata,
    Column('anime_id', Integer, ForeignKey('anime.id'), primary_key=True),
    Column('genre_id', Integer, ForeignKey('genre.id'), primary_key=True)
)

onair_genre = Table(
    'onair_genre',
    db.metadata,
    Column('onair_id', Integer, ForeignKey('on_air.id'), primary_key=True),
    Column('genre_id', Integer, ForeignKey('genre.id'), primary_key=True)
)