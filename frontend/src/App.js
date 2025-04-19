import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import YouTube from "react-youtube";
import { FaRandom, FaPlus, FaSearch, FaMusic, FaPlay, FaPause, FaStop, FaTv } from "react-icons/fa";
import "./App.css";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

function App() {
  const [theme, setTheme] = useState("");
  const [currentVideoIndex, setCurrentVideoIndex] = useState(0);
  const [playlist, setPlaylist] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isTvOn, setIsTvOn] = useState(false);
  const [isStaticEffect, setIsStaticEffect] = useState(false);
  const [videoError, setVideoError] = useState(false);
  const playerRef = useRef(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!theme.trim()) return;

    setIsLoading(true);
    setError(null);
    setVideoError(false);
    setIsTvOn(false);
    setIsStaticEffect(true);
    
    try {
      const response = await axios.post(`${BACKEND_URL}/api/generate-playlist`, {
        theme: theme,
        count: 10
      });
      
      setPlaylist(response.data.playlist);
      setCurrentVideoIndex(0);
      
      // TV turn on effect
      setTimeout(() => {
        setIsStaticEffect(false);
        setIsTvOn(true);
      }, 1500);
      
    } catch (err) {
      console.error("Error fetching playlist:", err);
      setError("Failed to generate playlist. Please try again.");
      setIsStaticEffect(false);
    } finally {
      setIsLoading(false);
    }
  };

  const handleVideoEnd = () => {
    // Go to next video when current one ends
    if (currentVideoIndex < playlist.length - 1) {
      setCurrentVideoIndex(currentVideoIndex + 1);
    } else {
      // Loop back to beginning
      setCurrentVideoIndex(0);
    }
  };

  const handleRandomSong = () => {
    if (playlist.length > 0) {
      setIsStaticEffect(true);
      setTimeout(() => {
        const randomIndex = Math.floor(Math.random() * playlist.length);
        setCurrentVideoIndex(randomIndex);
        setIsStaticEffect(false);
      }, 500);
    }
  };

  const openYouTube = () => {
    if (playlist.length > 0) {
      const videoId = playlist[currentVideoIndex].videoId;
      window.open(`https://www.youtube.com/watch?v=${videoId}`, '_blank');
    }
  };

  const togglePlay = () => {
    if (playerRef.current) {
      if (isPlaying) {
        playerRef.current.internalPlayer.pauseVideo();
      } else {
        playerRef.current.internalPlayer.playVideo();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handlePlayerReady = (event) => {
    // Save the player reference
    playerRef.current = event.target;
  };

  const handlePlayerStateChange = (event) => {
    // Update isPlaying based on YouTube player state
    // 1 = playing, 2 = paused, 0 = ended
    setIsPlaying(event.data === 1);
    if (event.data === 0) {
      handleVideoEnd();
    }
  };

  return (
    <div className="app-container">
      <div className="tv-container">
        <div className="tv-frame">
          <div className="tv-antenna left"></div>
          <div className="tv-antenna right"></div>
          
          <div className="tv-screen-container">
            <div className={`tv-screen ${isTvOn ? 'on' : 'off'} ${isStaticEffect ? 'static' : ''}`}>
              {playlist.length > 0 && isTvOn ? (
                <>
                  <YouTube
                    videoId={playlist[currentVideoIndex].videoId}
                    opts={{
                      width: '100%',
                      height: '100%',
                      playerVars: {
                        autoplay: 1,
                        controls: 1, // Enable controls for better user experience
                        showinfo: 0,
                        rel: 0,
                        iv_load_policy: 3,
                        modestbranding: 1,
                        origin: window.location.origin // Add origin for security
                      },
                    }}
                    onReady={handlePlayerReady}
                    onStateChange={handlePlayerStateChange}
                    onEnd={handleVideoEnd}
                    className="youtube-player"
                    onError={(e) => {
                      console.error("YouTube Player Error:", e);
                      setVideoError(true);
                    }}
                  />
                  {videoError && (
                    <div className="video-error-overlay">
                      <p>Video unavailable. Try another song or open directly in YouTube.</p>
                    </div>
                  )}
                </>
              ) : isStaticEffect ? (
                <div className="static-effect"></div>
              ) : (
                <div className="tv-screen-off">
                  <FaTv size={60} />
                  <p>Enter a theme to generate your mixtape</p>
                </div>
              )}
            </div>
          </div>
          
          <div className="tv-controls">
            <div className="tv-knobs">
              <div className="tv-knob"></div>
              <div className="tv-knob"></div>
            </div>
          </div>
          
          {/* Removed TV control buttons as requested */}
        </div>
        
        <div className="tv-stand"></div>
      </div>
      
      <div className="mixtape-controls">
        <h1 className="app-title">90s MTV Mixtape Generator</h1>
        <form onSubmit={handleSubmit} className="theme-form">
          <div className="input-group">
            <input
              type="text"
              value={theme}
              onChange={(e) => setTheme(e.target.value)}
              placeholder="Enter your music theme (e.g., grunge, pop, hip hop)"
              disabled={isLoading}
              className="theme-input"
            />
            <button type="submit" className="submit-btn" disabled={isLoading || !theme.trim()}>
              {isLoading ? "Generating..." : <FaSearch />}
            </button>
          </div>
        </form>
        
        {error && <div className="error-message">{error}</div>}
        
        {playlist.length > 0 && (
          <div className="playlist-container">
            <h2 className="playlist-title">Your 90s Mixtape</h2>
            <div className="playlist">
              {playlist.map((song, index) => (
                <div 
                  key={index} 
                  className={`playlist-item ${index === currentVideoIndex ? 'active' : ''}`}
                  onClick={() => {
                    setIsStaticEffect(true);
                    setTimeout(() => {
                      setCurrentVideoIndex(index);
                      setIsStaticEffect(false);
                    }, 500);
                  }}
                >
                  <div className="song-thumbnail">
                    <img src={song.thumbnail} alt={song.title} />
                    {index === currentVideoIndex && <div className="now-playing">Now Playing</div>}
                  </div>
                  <div className="song-info">
                    <div className="song-title">{song.title}</div>
                    <div className="song-artist">{song.artist}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
