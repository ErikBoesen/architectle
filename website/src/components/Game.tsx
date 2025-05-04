import React, { useEffect, useState } from 'react';

import Guesses from './Guesses';
import Footer from './Footer';

const CITIES = {
  all: 'All',
  nyc: 'New York City',
  chicago: 'Chicago',
  la: 'Los Angeles'
};

function Game() {
  const [buildingsAll, setBuildingsAll] = useState([]);
  const [buildingsQueue, setBuildingsQueue] = useState([]);
  const [lives, setLives] = useState(100);
  const [round, setRound] = useState(0);
  const [userGuess, setUserGuess] = useState(0);
  const [lastGuesses, setLastGuesses] = useState([]);
  const [showIntro, setShowIntro] = useState(false);
  const [showLossPopup, setShowLossPopup] = useState(false);
  const [selectedCity, setSelectedCity] = useState(null);

  useEffect(() => {
    const cityFromUrl = window.location.pathname.split('/')[1]; // Get city from URL
    if (cityFromUrl) {
      setSelectedCity(cityFromUrl);
    } else {
      setShowIntro(true);
    }
    const fetchBuildings = async () => {
      const response = await fetch('buildings.json');
      const data = await response.json();

      setBuildingsAll(data);
    };

    fetchBuildings();
  }, []);

  useEffect(() => {
    if (selectedCity) {
      window.history.pushState(null, '', `/${selectedCity.toLowerCase()}`);
    }
  }, [selectedCity]); // Update URL when selectedCity changes

  const fillBuildingQueue = (buildings, city) => {
    console.log('Current city selected ' + city);
    let queue = buildings.slice(); // Copy array
    if (city && city !== 'all') {
      queue = queue.filter(building => building.city === city);
    }
    // Shuffle buildings
    for (let i = queue.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [queue[i], queue[j]] = [queue[j], queue[i]]; // Swap elements
    }
    setBuildingsQueue(queue);
  };

  useEffect(() => {
    if (buildingsAll.length !== 0 && selectedCity !== null) {
      fillBuildingQueue(buildingsAll, selectedCity);
    }
  }, [buildingsAll, selectedCity])

  const handleCitySelection = (city) => {
    setSelectedCity(city);
    setShowIntro(false);
  };

  const handleGuess = () => {
    const correctYear = buildingsQueue[round].year;
    let difference = Math.abs(correctYear - userGuess);
    difference = 20 - difference;
    setLives(prevScore => Math.max(prevScore + difference, 0));
    setRound(prevIndex => (prevIndex + 1) % buildingsQueue.length); // Move to next building
    setUserGuess(0); // Reset user guess

    // Set last guess details
    const newGuess = {
        building: buildingsQueue[round],
        guessedYear: userGuess,
        difference: difference,
        correct: correctYear === userGuess,
    };

    setLastGuesses(prevGuesses => [newGuess, ...prevGuesses]); // Add new guess to the queue

    // Dismiss last guess message after 5 seconds
    setTimeout(() => {
        setLastGuesses(prevGuesses => prevGuesses.slice(0, prevGuesses.length - 1)); // Remove the oldest guess
    }, 5000);

    if (lives <= 0) {
      setShowLossPopup(true);
    }
  };

  const restartGame = () => {
    fillBuildingQueue(buildingsAll, selectedCity);
    setLives(100);
    setRound(0);
    setUserGuess(0);
    setLastGuesses([]);
    setShowLossPopup(false);
    setShowIntro(false);
  };

  const copyToClipboard = () => {
    const performanceRecord = `I made it to round ${round}! architectle.com`;
    let emojiPerformance = '';

    lastGuesses.forEach(guess => {
        const difference = Math.abs(guess.building.year - guess.guessedYear);
        if (difference === 0) {
          emojiPerformance += '⭐️';
        } else if (difference > -10) {
          emojiPerformance += '🟩';
        } else if (difference > -20) {
          emojiPerformance += '🟨';
        } else if (difference > -40) {
          emojiPerformance += '🟧';
        } else {
          emojiPerformance += '🟥';
        }
    });

    const fullRecord = `${performanceRecord} ${emojiPerformance}`;
    navigator.clipboard.writeText(fullRecord);
    alert('Performance copied to clipboard!');
  };

  return (
    <div className='App'>
      <header>
        <div id='logo'>
          <img src='logo512.png' alt='Logo' />
          <h1>Architectle</h1>
        </div>
        <div id='scoring'>
          <p>{lives} ❤️</p>
          <p>{round} 🏆</p>
        </div>
      </header>
      <main>
        {buildingsQueue.length > 0 && (
          <div>
            <img className='photo' src={buildingsQueue[round].image} alt={buildingsQueue[round].name} />
            <p>{userGuess === 0 ? 'Guess the year this building was built:' : userGuess}</p>
            <label>
              <input
                type='range'
                min='1640'
                max='2025'
                value={userGuess}
                onChange={(e) => setUserGuess(Number(e.target.value))}
              />
            </label>
            <button onClick={handleGuess}>Guess</button>
            <Guesses guesses={lastGuesses} />
          </div>
        )}
      </main>

      {showIntro && (
        <div className={'instructions popup ' + (showIntro ? 'shown' : '')}>
          <div className='content'>
            <h2>How to Play</h2>
            <p>Guess the year each building was constructed based on its architectural style and other context clues. You have 100 lives, and you lose one for each year off you are from a correct answer. You can also get bonus points by guessing within the correct decade. Good luck!</p>
            <h3>Pick a city:</h3>
            {Object.keys(CITIES).map((slug) =>
              <button key={slug} onClick={() => handleCitySelection(slug)}>{CITIES[slug]}</button>
            )}
          </div>
        </div>
      )}

      <div className={'loss popup ' + (showLossPopup ? 'shown' : '')}>
        <div className='content'>
          <h2>Game over!</h2>
          <p>Congratulations! You made it to round {round}.</p>
          <button onClick={copyToClipboard}>Share</button>
          <button onClick={restartGame}>Restart Game</button>
          <button onClick={() => handleCitySelection(null)}>Switch Cities</button>
        </div>
      </div>

      <Footer />
    </div>
  );
}

export default Game;
