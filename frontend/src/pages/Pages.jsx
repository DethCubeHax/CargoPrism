import React from 'react';
import {Navigate, Route, Routes, useLocation} from "react-router-dom";
import Home from './Home';
import Performance from './Performance';
import MarketAnalysis from './Market';


function Pages() {
  const location = useLocation();
  return (
    <Routes location={location} key={location.pathname}>
        <Route path="/" element={<Home />} />
        <Route path="/metrics" element={<Performance />} />
        <Route path="/market" element={<MarketAnalysis />} />
    </Routes>
  )
}

export default Pages