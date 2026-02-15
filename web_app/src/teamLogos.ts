/**
 * Helper para obter escudos de times
 * Usando escudos locais salvos em /escudos/
 */

// Mapeamento de times para arquivos locais de escudos
const TEAM_LOGOS: Record<string, string> = {
  // Brasileirão Série A & Copa do Brasil
  'Flamengo': '/escudos/flamengo.png',
  'Palmeiras': '/escudos/palmeiras.png',
  'São Paulo': '/escudos/sao-paulo.png',
  'Corinthians': '/escudos/corinthians.png',
  'Atlético Mineiro': '/escudos/atletico-mineiro.png',
  'Fluminense': '/escudos/fluminense.png',
  'Botafogo': '/escudos/botafogo.png',
  'Grêmio': '/escudos/gremio.png',
  'Internacional': '/escudos/internacional.png',
  'Santos': '/escudos/santos.png',
  'Vasco': '/escudos/vasco.png',
  'Vasco da Gama': '/escudos/vasco.png',
  'Cruzeiro': '/escudos/cruzeiro.png',
  'Athletico Paranaense': '/escudos/athletico-paranaense.png',
  'Athletico-PR': '/escudos/athletico-paranaense.png',
  'Bahia': '/escudos/bahia.png',
  'Fortaleza': '/escudos/fortaleza.png',
  'Bragantino': '/escudos/bragantino.png',
  'Cuiabá': '/escudos/cuiaba.png',
  'Goiás': '/escudos/goias.png',
  'Coritiba': '/escudos/coritiba.png',
  'Atlético Goianiense': '/escudos/atletico-goianiense.png',

  // Premier League
  'Manchester City': '/escudos/manchester-city.png',
  'Arsenal': '/escudos/arsenal.png',
  'Liverpool': '/escudos/liverpool.png',
  'Manchester United': '/escudos/manchester-united.png',
  'Newcastle': '/escudos/newcastle.png',
  'Tottenham': '/escudos/tottenham.png',
  'Chelsea': '/escudos/chelsea.png',
  'Brighton': '/escudos/brighton.png',
  'Aston Villa': '/escudos/aston-villa.png',
  'West Ham': '/escudos/west-ham.png',
  'Fulham': '/escudos/fulham.png',
  'Brentford': '/escudos/brentford.png',
  'Crystal Palace': '/escudos/crystal-palace.png',
  'Wolverhampton': '/escudos/wolverhampton.png',
  'Nottingham Forest': '/escudos/nottingham-forest.png',
  'Everton': '/escudos/everton.png',
  'Leicester': '/escudos/leicester.png',
  'Leeds United': '/escudos/leeds-united.png',
  'Southampton': '/escudos/southampton.png',
  'Bournemouth': '/escudos/bournemouth.png',
};

// Logos de ligas/campeonatos
const LEAGUE_LOGOS: Record<string, string> = {
  'Brasileirão Série A': '🇧🇷',
  'Copa do Brasil': '🏆',
  'Copa Libertadores': '🏆',
  'Copa Sul-Americana': '🥈',
  'Campeonato Paulista': '⚽',
  'Campeonato Carioca': '⚽',
  'Campeonato Mineiro': '⚽',
  'Campeonato Gaúcho': '⚽',
};

/**
 * Retorna a URL do escudo do time
 * @param teamName Nome do time
 * @returns URL do escudo ou emoji padrão
 */
export function getTeamLogo(teamName: string): string {
  // Busca exata
  if (TEAM_LOGOS[teamName]) {
    return TEAM_LOGOS[teamName];
  }

  // Busca parcial (case-insensitive)
  const normalizedName = teamName.toLowerCase();
  const found = Object.keys(TEAM_LOGOS).find(key =>
    key.toLowerCase().includes(normalizedName) || normalizedName.includes(key.toLowerCase())
  );

  if (found) {
    return TEAM_LOGOS[found];
  }

  // Fallback: retorna emoji de escudo
  return '⚽';
}

/**
 * Retorna o emoji/logo da liga
 * @param leagueName Nome da liga
 * @returns Emoji ou string do logo
 */
export function getLeagueLogo(leagueName: string): string {
  return LEAGUE_LOGOS[leagueName] || '🏆';
}

/**
 * Verifica se uma URL de logo é válida (URL externa ou path local)
 * @param url URL ou path a verificar
 * @returns true se for uma URL válida ou path local
 */
export function isValidLogoUrl(url: string): boolean {
  return url.startsWith('http://') || url.startsWith('https://') || url.startsWith('/');
}

