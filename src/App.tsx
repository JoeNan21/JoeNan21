import { Route, Routes } from 'react-router-dom';
import { Layout } from './components/Layout';
import { Home } from './pages/Home';
import { Modules } from './pages/Modules';
import { CeremonyDetail } from './pages/CeremonyDetail';
import { ArticleDetail } from './pages/ArticleDetail';
import { Glossary } from './pages/Glossary';
import { Phrases } from './pages/Phrases';
import { Wizard } from './pages/Wizard';
import { Bookmarks } from './pages/Bookmarks';
import { Review } from './pages/Review';

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Home />} />
        <Route path="/modules" element={<Modules />} />
        <Route path="/ceremony/:id" element={<CeremonyDetail />} />
        <Route path="/article/:id" element={<ArticleDetail />} />
        <Route path="/glossary" element={<Glossary />} />
        <Route path="/phrases" element={<Phrases />} />
        <Route path="/wizard" element={<Wizard />} />
        <Route path="/bookmarks" element={<Bookmarks />} />
        <Route path="/review" element={<Review />} />
      </Route>
    </Routes>
  );
}
