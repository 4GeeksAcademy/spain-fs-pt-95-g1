import React, { useState, useEffect } from 'react';
import '../index.css';
import { useNavigate } from 'react-router-dom';

const Recommendations = ({ genres, currentAnimeId }) => {
    const [recommendedAnimes, setRecommendedAnimes] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const API_URL = import.meta.env.VITE_API_URL;
    const navigate = useNavigate();

    useEffect(() => {
        const fetchGenreRecommendations = async () => {
            if (!genres || genres.length === 0) {
                setLoading(false);
                return;
            }

            try {
                const response = await fetch(`${API_URL}/api/anime/${currentAnimeId}/recommendations/genres`);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const data = await response.json();
                setRecommendedAnimes(data.recommendations);
                setLoading(false);
            } catch (err) {
                setError(err.message);
                setLoading(false);
            }
        };

        fetchGenreRecommendations();
    }, [genres, currentAnimeId, navigate]);

    const goToAnimeDetails = (animeId) =>{
        navigate(`/anime/${animeId}`);
    };

    if (loading) {
        return <div className="recommendations-container justify-content-center mt-5">Cargando recomendaciones por género...</div>;
    }

    if (error) {
        return <div className="recommendations-container justify-content-center mt-5 text-danger">Error al cargar recomendaciones: {error}</div>;
    }

    return (
        <div className="recommendations-container justify-content-center ">
            <h2 className='recomendations-title d-flex justify-content-center '>Recommendations Based on Genres</h2>
            <div className="recommendations-list d-flex justify-content-center ">
                {recommendedAnimes.map((anime) => (
                    <div key={anime.id} className="recommendation-card" onClick={() => goToAnimeDetails(anime.id)}
                         style={{cursor: 'pointer'}}>
                        <img className='rounded' src={anime.image_url} alt={anime.title} />
                        <h3 className="title-anime">{anime.title}</h3>
                    </div>
                ))}
            </div>
        </div>
    );
};


export default Recommendations;