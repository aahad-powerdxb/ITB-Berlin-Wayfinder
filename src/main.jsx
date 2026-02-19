import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './views/App.jsx'
import './css/index.css'

import { StateProvider } from "./context/StateContext";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <StateProvider>
      <App />
    </StateProvider>
  </React.StrictMode>
);
