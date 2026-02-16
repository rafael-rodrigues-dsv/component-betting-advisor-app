/**
 * QuickGuide - Guia rápido de como usar o sistema
 */
import React from 'react';

export const QuickGuide: React.FC = () => {
  return (
    <div className="quick-guide">
      <h3>🚀 Como usar</h3>
      <ol>
        <li>
          <span className="step-number">1</span>
          <span className="step-text">
            Vá para <strong>Jogos</strong> e selecione as partidas que deseja analisar
          </span>
        </li>
        <li>
          <span className="step-number">2</span>
          <span className="step-text">
            Escolha uma estratégia (Balanceada, Conservadora, Value Bet ou Agressiva)
          </span>
        </li>
        <li>
          <span className="step-number">3</span>
          <span className="step-text">
            Clique em <strong>Analisar</strong> e aguarde as previsões serem geradas
          </span>
        </li>
        <li>
          <span className="step-number">4</span>
          <span className="step-text">
            Na aba <strong>Previsões</strong>, revise as sugestões e adicione ao bilhete
          </span>
        </li>
        <li>
          <span className="step-number">5</span>
          <span className="step-text">
            Em <strong>Bilhetes</strong>, defina o valor da aposta e crie o bilhete
          </span>
        </li>
        <li>
          <span className="step-number">6</span>
          <span className="step-text">
            Aguarde 5 segundos para o resultado ser processado automaticamente! 🎉
          </span>
        </li>
      </ol>
    </div>
  );
};

