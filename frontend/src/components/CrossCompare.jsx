import { useState, useEffect } from 'react'

function CrossCompare() {
  const [teamsData, setTeamsData] = useState(null)
  const [team1, setTeam1] = useState('')
  const [year1, setYear1] = useState('')
  const [team2, setTeam2] = useState('')
  const [year2, setYear2] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // Carregar lista de times/anos disponíveis
  useEffect(() => {
    fetch('/api/teams-years')
      .then(res => res.json())
      .then(data => setTeamsData(data))
      .catch(err => console.error('Erro ao carregar times:', err))
  }, [])

  const handleCompare = async () => {
    if (!team1 || !year1 || !team2 || !year2) {
      setError('Selecione ambos os times e anos')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await fetch(
        `/api/compare-cross?team1=${encodeURIComponent(team1)}&year1=${year1}&team2=${encodeURIComponent(team2)}&year2=${year2}`
      )

      if (!response.ok) {
        const err = await response.json()
        throw new Error(err.detail || 'Erro na comparação')
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const getYearsForTeam = (teamName) => {
    if (!teamsData) return []
    const team = teamsData.teams.find(t => t.name === teamName)
    return team ? team.years : []
  }

  const getConfidenceColor = (confidence) => {
    switch (confidence) {
      case 'high': return 'text-emerald-400 bg-emerald-500/20 border-emerald-500/30'
      case 'medium': return 'text-amber-400 bg-amber-500/20 border-amber-500/30'
      case 'low': return 'text-red-400 bg-red-500/20 border-red-500/30'
      default: return 'text-slate-400 bg-slate-500/20 border-slate-500/30'
    }
  }

  const getConfidenceLabel = (confidence) => {
    switch (confidence) {
      case 'high': return 'Alta confiança'
      case 'medium': return 'Média confiança'
      case 'low': return 'Baixa confiança'
      default: return confidence
    }
  }

  const getSimilarityColor = (sim) => {
    if (sim >= 0.8) return 'text-emerald-400'
    if (sim >= 0.6) return 'text-green-400'
    if (sim >= 0.4) return 'text-amber-400'
    if (sim >= 0.2) return 'text-orange-400'
    return 'text-red-400'
  }

  return (
    <div className="space-y-6">
      {/* Seletores */}
      <div className="bg-slate-800/70 backdrop-blur-sm rounded-2xl p-6 border border-slate-700/50">
        <h3 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
          <span className="w-1 h-6 bg-purple-500 rounded-full"></span>
          Comparar Seleções
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Time 1 */}
          <div className="space-y-3">
            <label className="block text-sm font-medium text-slate-400">Seleção 1</label>
            <select
              value={team1}
              onChange={(e) => { setTeam1(e.target.value); setYear1('') }}
              className="w-full bg-slate-700/80 text-white px-4 py-3 rounded-xl border border-slate-600/50 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 outline-none"
            >
              <option value="">Selecione...</option>
              {teamsData?.teams.map(team => (
                <option key={team.name} value={team.name}>{team.name}</option>
              ))}
            </select>

            <select
              value={year1}
              onChange={(e) => setYear1(e.target.value)}
              disabled={!team1}
              className="w-full bg-slate-700/80 text-white px-4 py-3 rounded-xl border border-slate-600/50 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 outline-none disabled:opacity-50"
            >
              <option value="">Ano da Copa...</option>
              {getYearsForTeam(team1).map(y => (
                <option key={y.year} value={y.year}>
                  {y.year} ({y.source === 'statsbomb' ? 'Completo' : 'Histórico'})
                </option>
              ))}
            </select>
          </div>

          {/* VS */}
          <div className="hidden md:flex items-center justify-center">
            <div className="text-3xl font-bold text-slate-600">VS</div>
          </div>

          {/* Time 2 */}
          <div className="space-y-3 md:col-start-2 md:row-start-1">
            <label className="block text-sm font-medium text-slate-400">Seleção 2</label>
            <select
              value={team2}
              onChange={(e) => { setTeam2(e.target.value); setYear2('') }}
              className="w-full bg-slate-700/80 text-white px-4 py-3 rounded-xl border border-slate-600/50 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 outline-none"
            >
              <option value="">Selecione...</option>
              {teamsData?.teams.map(team => (
                <option key={team.name} value={team.name}>{team.name}</option>
              ))}
            </select>

            <select
              value={year2}
              onChange={(e) => setYear2(e.target.value)}
              disabled={!team2}
              className="w-full bg-slate-700/80 text-white px-4 py-3 rounded-xl border border-slate-600/50 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 outline-none disabled:opacity-50"
            >
              <option value="">Ano da Copa...</option>
              {getYearsForTeam(team2).map(y => (
                <option key={y.year} value={y.year}>
                  {y.year} ({y.source === 'statsbomb' ? 'Completo' : 'Histórico'})
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Botão Comparar */}
        <div className="mt-6 flex justify-center">
          <button
            onClick={handleCompare}
            disabled={loading || !team1 || !year1 || !team2 || !year2}
            className="px-8 py-3 bg-gradient-to-r from-purple-600 to-purple-500 text-white font-medium rounded-xl shadow-lg shadow-purple-500/25 hover:shadow-purple-500/40 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Comparando...' : 'Comparar'}
          </button>
        </div>

        {error && (
          <div className="mt-4 p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm">
            {error}
          </div>
        )}
      </div>

      {/* Resultado */}
      {result && (
        <div className="bg-slate-800/70 backdrop-blur-sm rounded-2xl p-6 border border-slate-700/50">
          {/* Score Principal */}
          <div className="text-center mb-8">
            <div className="flex items-center justify-center gap-8 mb-4">
              {/* Time 1 */}
              <div className="text-center">
                <img
                  src={result.team1.flag_url}
                  alt={result.team1.name}
                  className="w-16 h-12 object-cover rounded-lg shadow-lg mx-auto mb-2"
                />
                <div className="text-white font-semibold">{result.team1.name}</div>
                <div className="text-slate-400 text-sm">{result.team1.year}</div>
              </div>

              {/* Similaridade */}
              <div>
                <div className={`text-5xl font-bold ${getSimilarityColor(result.similarity)}`}>
                  {(result.similarity * 100).toFixed(0)}%
                </div>
                <div className="text-slate-500 text-sm mt-1">similaridade</div>
              </div>

              {/* Time 2 */}
              <div className="text-center">
                <img
                  src={result.team2.flag_url}
                  alt={result.team2.name}
                  className="w-16 h-12 object-cover rounded-lg shadow-lg mx-auto mb-2"
                />
                <div className="text-white font-semibold">{result.team2.name}</div>
                <div className="text-slate-400 text-sm">{result.team2.year}</div>
              </div>
            </div>

            {/* Badge de confiança */}
            <div className="flex justify-center gap-2">
              <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getConfidenceColor(result.confidence)}`}>
                {getConfidenceLabel(result.confidence)}
              </span>
              <span className="px-3 py-1 rounded-full text-xs font-medium border border-slate-600 text-slate-400">
                {result.n_features} features comparadas
              </span>
            </div>
          </div>

          {/* Aviso de confiança baixa/média */}
          {result.confidence !== 'high' && (
            <div className="mb-6 p-4 bg-amber-500/10 border border-amber-500/20 rounded-xl">
              <p className="text-sm text-amber-200/80 flex items-start gap-2">
                <svg className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>
                  {result.confidence === 'low'
                    ? 'Comparação com poucas features em comum. Os dados disponíveis são limitados para estas edições.'
                    : 'Comparação baseada em dados históricos básicos. Features táticas avançadas não disponíveis para uma ou ambas as edições.'
                  }
                </span>
              </p>
            </div>
          )}

          {/* Tabela de comparação */}
          <div className="space-y-3">
            <h4 className="text-sm font-medium text-slate-400 uppercase tracking-wide">
              Comparação Feature a Feature
            </h4>
            <div className="space-y-2">
              {result.feature_comparison.map((feature) => {
                const diff = Math.abs(feature.team1_value - feature.team2_value)
                const maxVal = Math.max(feature.team1_value, feature.team2_value)
                const diffPct = maxVal > 0 ? (diff / maxVal) * 100 : 0

                return (
                  <div
                    key={feature.name}
                    className="flex items-center gap-4 p-3 bg-slate-700/30 rounded-xl"
                  >
                    <div className="w-32 text-sm text-slate-400">{feature.display_name}</div>
                    <div className="flex-1 flex items-center gap-4">
                      <div className="w-20 text-right text-white font-medium">
                        {feature.team1_value.toFixed(1)}{feature.unit}
                      </div>
                      <div className="flex-1 h-2 bg-slate-600/50 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-purple-500 to-purple-400 rounded-full"
                          style={{ width: `${Math.min(100, (feature.team1_value / maxVal) * 100)}%` }}
                        />
                      </div>
                      <div className="flex-1 h-2 bg-slate-600/50 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-amber-500 to-amber-400 rounded-full"
                          style={{ width: `${Math.min(100, (feature.team2_value / maxVal) * 100)}%` }}
                        />
                      </div>
                      <div className="w-20 text-white font-medium">
                        {feature.team2_value.toFixed(1)}{feature.unit}
                      </div>
                    </div>
                    <div className={`w-16 text-right text-xs ${diffPct > 20 ? 'text-amber-400' : 'text-slate-500'}`}>
                      {diffPct > 0 ? `${diffPct.toFixed(0)}% diff` : '-'}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Features ausentes */}
          {result.features_missing && result.features_missing.length > 0 && (
            <div className="mt-4 p-3 bg-slate-700/20 rounded-xl">
              <h5 className="text-xs font-medium text-slate-500 uppercase tracking-wide mb-2">
                Features nao disponiveis ({result.features_missing.length})
              </h5>
              <div className="flex flex-wrap gap-2">
                {result.features_missing.map(f => (
                  <span key={f} className="text-xs text-slate-500 bg-slate-700/50 px-2 py-1 rounded">
                    {f.replace(/_/g, ' ')}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Fontes */}
          <div className="mt-6 pt-4 border-t border-slate-700/50 flex justify-center gap-6 text-xs text-slate-500">
            <div>
              <span className="text-slate-600">Fonte {result.team1.name}:</span>{' '}
              <span className="text-slate-400">{result.team1.source === 'statsbomb' ? 'StatsBomb' : 'Dados Historicos'}</span>
            </div>
            <div>
              <span className="text-slate-600">Fonte {result.team2.name}:</span>{' '}
              <span className="text-slate-400">{result.team2.source === 'statsbomb' ? 'StatsBomb' : 'Dados Historicos'}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default CrossCompare
