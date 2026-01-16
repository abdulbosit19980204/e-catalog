import React from "react";
import AgentTracker from "./admin/AgentTracker";
import "./AgentTrackerPage.css";

const AgentTrackerPage = () => {
  return (
    <div className="standalone-tracker-page">
      <main className="tracker-main">
        <AgentTracker />
      </main>
    </div>
  );
};

export default AgentTrackerPage;
