import React, { useState, useEffect, useContext } from 'react';
import '../css/FinalProject.css';
import { useParams } from 'react-router-dom';
import Recommendations from './Recommendations';
import { UserContext } from '../context/UserContext'; 

function AnimeCard() {
    const { id } = useParams();
    const [animeDetails, setAnimeDetails] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [isFavorite, setIsFavorite] = useState(false);
    const [isWatching, setIsWatching] = useState(false);
    const [likes, setLikes] = useState(0);
    const [hasLiked, setHasLiked] = useState(false);
    const API_URL = import.meta.env.VITE_BACKEND_URL;
    const { isLogged, token } = useContext(UserContext); 


    useEffect(() => {
        const fetchAnimeDetails = async () => {
            setLoading(true);
            setError(null);
            setAnimeDetails(null);

            try {
                const response = await fetch(`${API_URL}api/anime/${id}`);
                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(`HTTP error! status: ${response.status} - ${errorData?.message || 'Error al cargar los detalles del anime'}`);
                }
                const data = await response.json();
                setAnimeDetails(data);
                setLoading(false);

                if (isLogged) {
                    fetchUserPreferences();
                }

            } catch (e) {
                setError(e);
                setLoading(false);
            }
        };

        fetchAnimeDetails();
    }, [id, isLogged, API_URL]);

    const fetchUserPreferences = async () => {
        try {
            const favoriteResponse = await fetch(`${API_URL}api/favorites/${id}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            const watchingResponse = await fetch(`${API_URL}api/watching/${id}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (favoriteResponse.ok) {
                const favoriteData = await favoriteResponse.json();
                setIsFavorite(favoriteData.isFavorite);
            }
            if (watchingResponse.ok) {
                const watchingData = await watchingResponse.json();
                setIsWatching(watchingData.isWatching);
            }

        } catch (error) {
            console.error("Error fetching user preferences:", error);
        }
    };

    const handleFavoriteClick = async () => {
        if (!isLogged) {
            alert("Debes estar logueado para añadir a favoritos.");
            return;
        }

        try {
            const response = await fetch(`${API_URL}api/favorites/${id}`, {
                method: isFavorite ? 'DELETE' : 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(`Failed to update favorites: ${response.status} - ${errorData?.message || 'Error al actualizar favoritos'}`);
            }

            setIsFavorite(!isFavorite);
        } catch (error) {
            console.error("Error updating favorites:", error);
        }
    };

    const handleWatchingClick = async () => {
        if (!isLogged) {
            alert("Debes estar logueado para añadir a tu lista de viendo.");
            return;
        }

        try {
            const response = await fetch(`${API_URL}api/watching/${id}`, {
                method: isWatching ? 'DELETE' : 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(`Failed to update watching: ${response.status} - ${errorData?.message || 'Error al actualizar la lista de viendo'}`);
            }

            setIsWatching(!isWatching);
        } catch (error) {
            console.error("Error updating watching:", error);
        }
    };

    const handleTrailerClick = () => {
        const trailerUrl = animeDetails?.trailer?.url || 'https://www.youtube.com/watch?v=K9Gnl0VeIVI';
        window.open(trailerUrl, '_blank');
    };

    const handleLikeClick = () => {
        if (!isLogged) {
            alert("Debes estar logueado para dar me gusta.");
            return;
        }
        setLikes(hasLiked ? likes - 1 : likes + 1);
        setHasLiked(!hasLiked);
    };

    if (loading) {
        return <div>Cargando detalles del anime...</div>;
    }

    if (error) {
        return <div>Error al cargar los detalles del anime: {error.message}</div>;
    }

    if (!animeDetails) {
        return <div>No se encontraron detalles para este anime.</div>;
    }

    return (
        <div className='container'>
            <div className="anime-card ">
                <div className='container-image'>
                    <img src={animeDetails.image_url} alt={animeDetails.title} id='imagen_anime' className="cover-image w-auto" />
                    <div className='buttons-card'>
                        <button className={`favorite-button ${isFavorite ? 'active' : ''}`} onClick={handleFavoriteClick} title={isFavorite ? 'Eliminar de favoritos' : 'Añadir a Favoritos'} >
                            <i className={`fa-solid fa-heart ${isFavorite ? 'text-danger' : ''}`}></i>
                        </button>

                        <button
                            className={`watching-button ${isWatching ? 'active' : ''} `} onClick={handleWatchingClick}
                            title={isWatching ? 'Dejar de ver' : 'Añadir a viendo'} >
                            <i className={`fa-solid ${isWatching ? 'fa-eye-slash' : 'fa-eye'}`}
                                style={{ color: isWatching ? 'purple' : '' }}></i>
                        </button>
                        {animeDetails?.trailer?.url && (
                            <button className="trailer-button" onClick={handleTrailerClick} title='Trailer'>
                                <i className="fa-solid fa-clapperboard"></i>
                            </button>
                        )}
                    </div>
                    <div className="likes-container">ME GUSTA!
                        <button className={`like-button ${hasLiked ? 'liked' : ''}`} onClick={handleLikeClick} title={hasLiked ? 'Quitar me gusta' : 'Me gusta'}>
                            <i className="fa-solid fa-thumbs-up"></i>
                        </button>
                        <span className="like-count">{likes}</span>
                    </div>
                </div>

                <div className='card-body px-3'>
                    <h1>{animeDetails.title}</h1>
                    <p className="synopsis">{animeDetails.synopsis}</p>
                    <div className="anime-details-info">
                        <ul className="anime-details-list">
                            <li className="genres-list-item">
                                <strong>Género: </strong>
                                {animeDetails.genres && animeDetails.genres.map((genre) => (
                                    <span key={genre.id} className="genre">
                                        {genre.name} {animeDetails.genres.indexOf(genre) < animeDetails.genres.length - 1 ? ', ' : ''}
                                    </span>
                                ))}
                            </li>
                            <li className="estado-list-item">
                                <strong>Estado:</strong> {animeDetails.airing ? 'En emisión' : 'Finalizado'}
                            </li>
                            <li className="puntuacion-list-item">
                                <strong>Puntuación:</strong> {animeDetails.score !== null ? animeDetails.score : 'No disponible'}
                            </li>
                            <li className="episodios-list-item">
                                <strong>Episodios:</strong> {animeDetails.episodes !== null ? animeDetails.episodes : 'No disponible'}
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
            {animeDetails.genres && <Recommendations genres={animeDetails.genres} currentAnimeId={parseInt(id)} />}
        </div>

    );
}

export default AnimeCard;