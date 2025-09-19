import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "./components/ui/sonner";
import Home from "./components/Home";
import JobDetails from "./components/JobDetails";
import Candidates from "./components/Candidates";
import JobCandidates from "./components/JobCandidates";
import Layout from "./components/Layout";

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/jobs/:id" element={<JobDetails />} />
            <Route path="/jobs/:id/candidates" element={<JobCandidates />} />
            <Route path="/candidates" element={<Candidates />} />
          </Routes>
        </Layout>
      </BrowserRouter>
      <Toaster />
    </div>
  );
}

export default App;