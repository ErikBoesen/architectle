import React, { useEffect, useState } from 'react';

function Guesses({ guesses }) {

    const getClasses = (difference) => {
        let classes = ['guess'];
        if (difference === 0) {
            classes.push('blue')
        } else if (difference > -10) {
            classes.push('green');
        } else if (difference > -20) {
            classes.push('yellow');
        } else if (difference > -40) {
            classes.push('orange');
        } else {
            classes.push('red');
        }
        return classes.join(' ');
    };

    return (
        <div className='guesses'>
            {guesses.map((guess, index) => (
            <div key={index} className={getClasses(guess.difference)}>
                <p>
                    <a href={'https://en.wikipedia.org/wiki/' + guess.building.name.replace(' ', '_')}>{guess.building.name}</a> was finished in {guess.building.year}, you guessed {guess.guessedYear}. {guess.correct ? 'Perfect guess!' : `${guess.difference} lives!`}
                </p>
            </div>
            ))}
        </div>
    );
}

export default Guesses;
