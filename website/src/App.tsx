import React, { useEffect, useState } from 'react';
import Guesses from './components/Guesses';
import './App.css';

function App() {
  const [buildings, setBuildings] = useState([]);
  const [lives, setLives] = useState(100);
  const [round, setRound] = useState(0);
  const [userGuess, setUserGuess] = useState(0);
  const [lastGuesses, setLastGuesses] = useState([]);
  const [showInstructions, setShowInstructions] = useState(true);
  const [showLossPopup, setShowLossPopup] = useState(false);

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
    let difference = Math.abs(correctYear - userGuess);
    difference = 10 - difference;
    setLives(prevScore => Math.max(prevScore + difference, 0));
    setRound(prevIndex => (prevIndex + 1) % buildings.length); // Move to next building
    setUserGuess(0); // Reset user guess

    // Set last guess details
    const newGuess = {
        building: buildings[round],
        guessedYear: userGuess,
        difference: difference,
        correct: correctYear === userGuess,
    };

    setLastGuesses(prevGuesses => [...prevGuesses, newGuess]); // Add new guess to the queue

    // Dismiss last guess message after 5 seconds
    setTimeout(() => {
        setLastGuesses(prevGuesses => prevGuesses.slice(1)); // Remove the oldest guess
    }, 5000);

    if (lives <= 0) {
      setShowLossPopup(true);
    }
  };

  const restartGame = () => {
    setLives(100);
    setRound(0);
    setUserGuess(0);
    setLastGuesses([]);
    setShowLossPopup(false);
    setShowInstructions(false);
  };

  const copyToClipboard = () => {
    const performanceRecord = `You made it to round ${round} with ${lives} lives left!`;
    navigator.clipboard.writeText(performanceRecord);
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
        {buildings.length > 0 && (
          <div>
            <img className='photo' src={buildings[round].image} alt={buildings[round].name} />
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

      {showInstructions && (
        <div className={'instructions popup ' + (showInstructions ? 'shown' : '')}>
          <div className='content'>
            <h2>How to Play</h2>
            <p>Guess the year each NYC building was constructed based on its architectural style and other context clues. You have 100 lives, and you lose one for each year off you are from a correct answer. You can also get bonus points by guessing witin the correct decade. Good luck!</p>
            <button onClick={() => setShowInstructions(false)}>Play</button>
          </div>
        </div>
      )}

      <div className={'loss popup ' + (showLossPopup ? 'shown' : '')}>
        <div className='content'>
          <h2>You Lost!</h2>
          <p>Congratulations! You made it to round {round}.</p>
          <button onClick={restartGame}>Restart Game</button>
          <button onClick={copyToClipboard}>Share</button>
        </div>
      </div>

      <footer>A game by <a href="https://erikboesen.com">Erik Boesen</a>.</footer>
    </div>
  );
}

export default App;
