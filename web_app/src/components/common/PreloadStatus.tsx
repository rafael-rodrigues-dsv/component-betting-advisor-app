import { useEffect, useState } from 'react';

/**
 * PreloadStatus - Indicador de pré-carregamento das ligas.
 *
 * Exibe uma notificação discreta informando que os dados já foram pré-carregados.
 */
export const PreloadStatus = () => {
  const [show, setShow] = useState(false);
  const [preloadInfo, setPreloadInfo] = useState<{
    hasCache: boolean;
    leagues: string[];
    timestamp: string;
  } | null>(null);

  useEffect(() => {
    checkPreloadStatus();
  }, []);

  const checkPreloadStatus = async () => {
    try {
      // Verifica se tem dados pré-carregados
      const response = await fetch('http://localhost:8000/api/v1/preload/status');

      if (response.ok) {
        const data = await response.json();
        setPreloadInfo(data);

        // Mostra notificação se tiver cache
        if (data.hasCache) {
          setShow(true);

          // Esconde após 5 segundos
          setTimeout(() => setShow(false), 5000);
        }
      }
    } catch (error) {
      console.log('Preload status check failed (expected in mock mode)');
    }
  };

  if (!show || !preloadInfo) return null;

  return (
    <div className="fixed bottom-4 right-4 bg-green-600 text-white px-4 py-3 rounded-lg shadow-lg z-50 animate-slide-in">
      <div className="flex items-center gap-3">
        <div className="flex-shrink-0">
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M13 10V3L4 14h7v7l9-11h-7z"
            />
          </svg>
        </div>

        <div className="flex-1">
          <p className="font-semibold text-sm">⚡ Dados Pré-carregados!</p>
          <p className="text-xs opacity-90">
            {preloadInfo.leagues.join(', ')} prontos para análise
          </p>
        </div>

        <button
          onClick={() => setShow(false)}
          className="flex-shrink-0 ml-2 hover:bg-green-700 rounded p-1 transition"
        >
          <svg
            className="w-4 h-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>
    </div>
  );
};

