import { createContext, useCallback, useContext, useEffect, useMemo, useState, ReactNode } from 'react';

interface BookmarkContextValue {
  bookmarks: string[];
  isBookmarked: (id: string) => boolean;
  toggle: (id: string) => void;
}

const BookmarkContext = createContext<BookmarkContextValue | null>(null);

const STORAGE_KEY = 'tautua:bookmarks';

export function BookmarkProvider({ children }: { children: ReactNode }) {
  const [bookmarks, setBookmarks] = useState<string[]>(() => {
    if (typeof window === 'undefined') return [];
    try {
      const raw = window.localStorage.getItem(STORAGE_KEY);
      return raw ? (JSON.parse(raw) as string[]) : [];
    } catch {
      return [];
    }
  });

  useEffect(() => {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(bookmarks));
  }, [bookmarks]);

  const toggle = useCallback((id: string) => {
    setBookmarks((prev) => (prev.includes(id) ? prev.filter((b) => b !== id) : [...prev, id]));
  }, []);

  const isBookmarked = useCallback((id: string) => bookmarks.includes(id), [bookmarks]);

  const value = useMemo(() => ({ bookmarks, isBookmarked, toggle }), [bookmarks, isBookmarked, toggle]);

  return <BookmarkContext.Provider value={value}>{children}</BookmarkContext.Provider>;
}

export function useBookmarks(): BookmarkContextValue {
  const ctx = useContext(BookmarkContext);
  if (!ctx) throw new Error('useBookmarks must be used within BookmarkProvider');
  return ctx;
}
