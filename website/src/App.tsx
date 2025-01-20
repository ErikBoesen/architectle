import React, { useEffect, useState } from 'react';
import './App.css';

function App() {
  const [buildings, setBuildings] = useState([]);

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

  return (
    <div className="App">
      <header>
        <h1>Architectle</h1>
      </header>
      <main>
        {buildings.map((building, index) => (
          <div key={index}>
            <h2>{building.name}</h2>
            <p>Year: {building.year}</p>
            <div>
              {building.images.map((image, imgIndex) => (
                <img key={imgIndex} src={image} alt={building.name} />
              ))}
            </div>
          </div>
        ))}
      </main>
    </div>
  );
}

export default App;
