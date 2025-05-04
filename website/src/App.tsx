import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';

import './App.css';

import Game from './components/Game';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/:city" element={<Game />} />
        <Route path="/" element={<Game />} />
      </Routes>
    </Router>
  );
}

export default App;
