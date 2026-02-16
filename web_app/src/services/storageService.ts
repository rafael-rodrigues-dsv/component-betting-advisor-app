/**
 * Storage Service - LocalStorage wrapper com tipagem
 */

const STORAGE_PREFIX = 'betting_advisor_';

export const storage = {
  /**
   * Salva um item no localStorage
   */
  set<T>(key: string, value: T): void {
    try {
      const serialized = JSON.stringify(value);
      localStorage.setItem(`${STORAGE_PREFIX}${key}`, serialized);
    } catch (error) {
      console.error(`Error saving to localStorage: ${key}`, error);
    }
  },

  /**
   * Recupera um item do localStorage
   */
  get<T>(key: string, defaultValue?: T): T | null {
    try {
      const item = localStorage.getItem(`${STORAGE_PREFIX}${key}`);
      if (!item) return defaultValue ?? null;
      return JSON.parse(item) as T;
    } catch (error) {
      console.error(`Error reading from localStorage: ${key}`, error);
      return defaultValue ?? null;
    }
  },

  /**
   * Remove um item do localStorage
   */
  remove(key: string): void {
    try {
      localStorage.removeItem(`${STORAGE_PREFIX}${key}`);
    } catch (error) {
      console.error(`Error removing from localStorage: ${key}`, error);
    }
  },

  /**
   * Limpa todos os itens do app
   */
  clear(): void {
    try {
      Object.keys(localStorage)
        .filter(key => key.startsWith(STORAGE_PREFIX))
        .forEach(key => localStorage.removeItem(key));
    } catch (error) {
      console.error('Error clearing localStorage', error);
    }
  },

  /**
   * Verifica se uma chave existe
   */
  has(key: string): boolean {
    return localStorage.getItem(`${STORAGE_PREFIX}${key}`) !== null;
  },
};

// Keys específicas para type-safety
export const STORAGE_KEYS = {
  SELECTED_BOOKMAKER: 'selected_bookmaker',
  SELECTED_LEAGUE: 'selected_league',
  STRATEGY: 'strategy',
  STAKE: 'stake',
  USER_PREFERENCES: 'user_preferences',
} as const;

