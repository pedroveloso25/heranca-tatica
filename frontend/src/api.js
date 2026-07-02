// Base URL da API - usa variavel de ambiente em producao, proxy local em dev
const API_BASE = import.meta.env.VITE_API_URL || ''

export async function fetchApi(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`
  const response = await fetch(url, options)

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Erro desconhecido' }))
    throw new Error(error.detail || `HTTP ${response.status}`)
  }

  return response.json()
}

export const api = {
  getTeams: () => fetchApi('/api/teams'),
  getCompare: (team) => fetchApi(`/api/compare?team=${encodeURIComponent(team)}`),
  getHistory: (team) => fetchApi(`/api/history?team=${encodeURIComponent(team)}`),
  getTeamsYears: () => fetchApi('/api/teams-years'),
  compareCross: (team1, year1, team2, year2) =>
    fetchApi(`/api/compare-cross?team1=${encodeURIComponent(team1)}&year1=${year1}&team2=${encodeURIComponent(team2)}&year2=${year2}`),
}
