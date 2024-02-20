/**
 * React Application Entry Point
 *
 * This file serves as the entry point for the React application.
 * It renders the root component of the application into the DOM.
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

// Create a root element for rendering the React application
const root = ReactDOM.createRoot(document.getElementById('root'));

// Render the root component of the application into the root element
root.render(
    <App />
);