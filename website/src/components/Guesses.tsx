import React, { useEffect, useState } from 'react';

function Guesses({ guesses }) {
  return (
    <div className='guesses'>
        {guesses.map((guess, index) => (
        <div key={index} className='guess'>
            <p>
            <a href={'https://en.wikipedia.org/wiki/' + guess.building.name.replace(' ', '_')}>{guess.building.name}</a> was finished in {guess.building.year}, you guessed {guess.guessedYear}. {guess.correct ? 'Perfect guess!' : `${guess.difference} lives!`}
            </p>
        </div>
        ))}
    </div>
  );
}

export default Guesses;
