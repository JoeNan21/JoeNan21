import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import { LanguageProvider } from './context/LanguageContext';
import { BookmarkProvider } from './context/BookmarkContext';
import './styles/index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <LanguageProvider>
      <BookmarkProvider>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </BookmarkProvider>
    </LanguageProvider>
  </React.StrictMode>
);
