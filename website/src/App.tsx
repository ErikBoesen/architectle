import React, { useEffect, useState } from 'react';
import './App.css';

function App() {
  const [buildings, setBuildings] = useState([]);
  const [lives, setLives] = useState(100);
  const [round, setRound] = useState(0);
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
    const correctYear = buildings[round].year;
    const difference = Math.abs(correctYear - userGuess);

    if (difference > 10) {
        setLives(prevScore => Math.max(prevScore - difference, 0)); // Subtract difference if greater than 10
    } else {
        setLives(prevScore => prevScore + (10 - difference), 10); // Add lives back for being within 10 years
    }

    setRound(prevIndex => (prevIndex + 1) % buildings.length); // Move to next building
    setUserGuess(0); // Reset user guess

    // Set last guess details
    setLastGuess({
        building: buildings[round],
        guessedYear: userGuess,
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
        <div id='scoring'>
          <p>{lives} ❤️</p>
          <p>{round} 🏆</p>
        </div>
      </header>
      <main>
        {buildings.length > 0 && (
          <div>
            {buildings[round].images.map((image, imgIndex) => (
                <img className='photo' key={imgIndex} src={image} alt={buildings[round].name} />
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
            {lastGuess && (
              <div>
                <p>
                   <a href={'https://en.wikipedia.org/wiki/' + lastGuess.building.name.replace(' ', '_')}>{lastGuess.building.name}</a> was finished in {lastGuess.building.year}, you guessed {lastGuess.guessedYear}. {lastGuess.correct ? 'Perfect guess!' : `-${lastGuess.difference} lives!`}
                </p>
              </div>
            )}
          </div>
        )}
      </main>
      <footer>A game by <a href="https://erikboesen.com">Erik Boesen</a>.</footer>
    </div>
  );
}

export default App;
