import React from 'react';
import {Navigate, Route, Routes, useLocation} from "react-router-dom";
import Home from './Home';


function Pages() {
  const location = useLocation();
  return (
    <Routes location={location} key={location.pathname}>
        <Route path="/" element={<Home />} />
    </Routes>
  )
}

export default Pages