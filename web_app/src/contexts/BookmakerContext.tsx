/**
 * BookmakerContext - Gerencia casas de apostas e seleção
 */
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import type { Bookmaker } from '../types';
import { matchesApi } from '../services/api';

interface BookmakerContextType {
  bookmakers: Bookmaker[];
  selectedBookmaker: string;
  loading: boolean;
  setSelectedBookmaker: (id: string) => void;
  getBookmakerName: (id: string) => string | undefined;
}

const BookmakerContext = createContext<BookmakerContextType | undefined>(undefined);

export const BookmakerProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [bookmakers, setBookmakers] = useState<Bookmaker[]>([]);
  const [selectedBookmaker, setSelectedBookmaker] = useState<string>('bet365');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadBookmakers();
  }, []);

  const loadBookmakers = async () => {
    setLoading(true);
    try {
      const data = await matchesApi.getBookmakers();
      setBookmakers(data.bookmakers || []);

      // Define o padrão como bet365 ou o primeiro da lista
      const defaultBookmaker = data.bookmakers?.find(b => b.is_default);
      if (defaultBookmaker) {
        setSelectedBookmaker(defaultBookmaker.id);
      }
    } catch (error) {
      console.error('Erro ao carregar casas de apostas:', error);
    } finally {
      setLoading(false);
    }
  };

  const getBookmakerName = (id: string): string | undefined => {
    return bookmakers.find(b => b.id === id)?.name;
  };

  return (
    <BookmakerContext.Provider
      value={{
        bookmakers,
        selectedBookmaker,
        loading,
        setSelectedBookmaker,
        getBookmakerName,
      }}
    >
      {children}
    </BookmakerContext.Provider>
  );
};

export const useBookmaker = (): BookmakerContextType => {
  const context = useContext(BookmakerContext);
  if (!context) {
    throw new Error('useBookmaker must be used within BookmakerProvider');
  }
  return context;
};

