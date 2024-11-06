import React from 'react';
import {Navigate, Route, Routes, useLocation} from "react-router-dom";
import Home from './Home';
import Performance from './Performance';


function Pages() {
  const location = useLocation();
  return (
    <Routes location={location} key={location.pathname}>
        <Route path="/" element={<Home />} />
        <Route path="/metrics" element={<Performance />} />
    </Routes>
  )
}

export default Pages