import React from "react";
import Navigation from "./Navigation";
import AgentTracker from "./admin/AgentTracker";
import "./AgentTrackerPage.css";

const AgentTrackerPage = () => {
  return (
    <div className="standalone-tracker-page">
      <Navigation />
      <main className="tracker-main">
        <AgentTracker />
      </main>
    </div>
  );
};

export default AgentTrackerPage;
