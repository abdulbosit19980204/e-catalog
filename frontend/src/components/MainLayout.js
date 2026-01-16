import React from 'react';
import { Outlet } from 'react-router-dom';
import Navigation from './Navigation';

const MainLayout = () => {
  return (
    <>
      <Navigation />
      <main className="App-main">
        <Outlet />
      </main>
    </>
  );
};

export default MainLayout;
