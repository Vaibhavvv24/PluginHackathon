import { useState } from "react";
import reactLogo from "./assets/react.svg";
import viteLogo from "/vite.svg";
import "./App.css";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import Video from "./pages/Video";
import Home from "./pages/Home";
import Navbar from "./components/nAVBAR.JSX";
import Signup from "./pages/Signup";
import Login from "./pages/Login";
import Assessment from "./pages/Assessment";
import PDF from "./pages/PDF";

function App() {
  return (
    <BrowserRouter>
      <div>
        <Navbar />
        <Routes>
          <Route path="/video" element={<Video />} />
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/take-assessment" element={<Assessment />} />
          <Route path="/pdf" element={<PDF />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
