import React, { useEffect, useState } from 'react';
import './App.css';

function App() {
  const [buildings, setBuildings] = useState([]);
  const [score, setScore] = useState(100);
  const [currentBuildingIndex, setCurrentBuildingIndex] = useState(0);
  const [userGuess, setUserGuess] = useState(0);
  const [lastGuess, setLastGuess] = useState(null);

  useEffect(() => {
    const fetchBuildings = async () => {
      const response = await fetch('buildings.json');
      const data = await response.json();
      // Shuffle the buildings array
      const shuffledBuildings = data.sort(() => Math.random() - 0.5);
      setBuildings(shuffledBuildings);
    };

    fetchBuildings();
  }, []);

  const handleGuess = () => {
    const correctYear = buildings[currentBuildingIndex].year;
    const difference = Math.abs(correctYear - userGuess);
    setScore(prevScore => Math.max(prevScore - difference, 0)); // Ensure score doesn't go below 0
    setCurrentBuildingIndex(prevIndex => (prevIndex + 1) % buildings.length); // Move to next building
    setUserGuess(0); // Reset user guess

    // Set last guess details
    setLastGuess({
      buildingName: buildings[currentBuildingIndex].name,
      guessedYear: userGuess,
      difference: difference,
      correct: correctYear === userGuess,
    });

    // Dismiss last guess message after 5 seconds
    setTimeout(() => {
      setLastGuess(null);
    }, 5000);
  };

  return (
    <div className='App'>
      <header>
        <div id='logo'>
          <img src='logo512.png' alt='Logo' />
          <h1>Architectle</h1>
        </div>
      </header>
      <main>
        {buildings.length > 0 && (
          <div>
            <h2>{buildings[currentBuildingIndex].name}</h2>
            {buildings[currentBuildingIndex].images.map((image, imgIndex) => (
                <img className='photo' key={imgIndex} src={image} alt={buildings[currentBuildingIndex].name} />
              ))}
            <p>{userGuess === 0 ? 'Guess the year this building was built:' : userGuess}</p>
            <label>
              <input
                type='range'
                min='1880'
                max='2025'
                value={userGuess}
                onChange={(e) => setUserGuess(Number(e.target.value))}
              />
            </label>
            <button onClick={handleGuess}>Guess</button>
            <p>Your score: {score}</p>
            {lastGuess && (
              <div>
                <p>
                  {lastGuess.correct ? "Congratulations!" : `You lost ${lastGuess.difference} points!`}
                </p>
                <p>
                  Last guess: {lastGuess.guessedYear} for {lastGuess.buildingName}
                </p>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
