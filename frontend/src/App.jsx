import { useState, useEffect } from 'react'
import TeamSelector from './components/TeamSelector'
import SimilarityBar from './components/SimilarityBar'
import TacticCard from './components/TacticCard'
import HistoryCard from './components/HistoryCard'
import CrossCompare from './components/CrossCompare'
import { api } from './api'

// Icone de trofeu
const TrophyIcon = () => (
  <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
    <path d="M6 9H4a2 2 0 01-2-2V5a2 2 0 012-2h2M18 9h2a2 2 0 002-2V5a2 2 0 00-2-2h-2M6 3h12v6a6 6 0 01-12 0V3zM12 15v4M8 21h8M9 19h6" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
)

function App() {
  const [teams, setTeams] = useState([])
  const [selectedTeam, setSelectedTeam] = useState(null)
  const [comparison, setComparison] = useState(null)
  const [history, setHistory] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('tatica')
  const [showOnlyReliable, setShowOnlyReliable] = useState(false)

  // Carregar lista de times
  useEffect(() => {
    api.getTeams()
      .then(data => setTeams(data.teams))
      .catch(err => setError('Erro ao carregar times'))
  }, [])

  // Carregar comparacao e historico quando selecionar time
  useEffect(() => {
    if (!selectedTeam) return

    setLoading(true)
    setError(null)
    setActiveTab('tatica')

    Promise.all([
      api.getCompare(selectedTeam),
      api.getHistory(selectedTeam).catch(() => null)
    ])
      .then(([compData, histData]) => {
        setComparison(compData)
        setHistory(histData)
        setLoading(false)
      })
      .catch(err => {
        setError(err.message)
        setLoading(false)
      })
  }, [selectedTeam])

  return (
    <div className="min-h-screen py-8 px-4">
      {/* Background decorativo */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-emerald-500/5 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-amber-500/5 rounded-full blur-3xl" />
      </div>

      <div className="max-w-4xl mx-auto relative">
        {/* Header com tema Copa */}
        <header className="text-center mb-10">
          <div className="inline-flex items-center justify-center gap-3 mb-4">
            <span className="text-amber-400">
              <TrophyIcon />
            </span>
            <h1 className="text-4xl md:text-5xl font-bold gold-gradient">
              Herança Tática
            </h1>
            <span className="text-amber-400">
              <TrophyIcon />
            </span>
          </div>
          <p className="text-slate-400 text-lg">
            Análise do DNA tático histórico das seleções da Copa do Mundo
          </p>
          <div className="mt-3 flex justify-center gap-1">
            {[1930, 1950, 1970, 1994, 2022].map(year => (
              <span key={year} className="text-xs text-slate-600 px-2 py-0.5 bg-slate-800/50 rounded">
                {year}
              </span>
            ))}
          </div>
        </header>

        <TeamSelector
          teams={teams}
          selectedTeam={selectedTeam}
          onSelect={setSelectedTeam}
          history={history}
        />

        {error && (
          <div className="bg-red-900/30 border border-red-500/50 text-red-200 px-4 py-3 rounded-xl mt-6 backdrop-blur-sm">
            {error}
          </div>
        )}

        {loading && (
          <div className="text-center mt-12">
            <div className="inline-block relative">
              <div className="animate-spin rounded-full h-12 w-12 border-4 border-amber-500/30 border-t-amber-500"></div>
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-6 h-6 bg-amber-500/20 rounded-full animate-pulse"></div>
              </div>
            </div>
            <p className="text-slate-400 mt-4">Analisando DNA tático...</p>
          </div>
        )}

        {/* Tabs - sempre visíveis */}
        {!loading && (
          <div className="mt-8 space-y-6">
            <div className="flex justify-center">
              <div className="inline-flex bg-slate-800/50 backdrop-blur-sm rounded-xl p-1.5 border border-slate-700/50">
                <button
                  onClick={() => setActiveTab('tatica')}
                  disabled={!comparison}
                  className={`px-6 py-2.5 rounded-lg font-medium transition-all duration-200 ${
                    activeTab === 'tatica' && comparison
                      ? 'bg-gradient-to-r from-emerald-600 to-emerald-500 text-white shadow-lg shadow-emerald-500/25'
                      : !comparison
                      ? 'text-slate-600 cursor-not-allowed'
                      : 'text-slate-400 hover:text-white hover:bg-slate-700/50'
                  }`}
                >
                  <span className="flex items-center gap-2">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                    Análise Tática
                  </span>
                </button>
                <button
                  onClick={() => setActiveTab('historico')}
                  disabled={!comparison}
                  className={`px-6 py-2.5 rounded-lg font-medium transition-all duration-200 ${
                    activeTab === 'historico' && comparison
                      ? 'bg-gradient-to-r from-amber-600 to-amber-500 text-white shadow-lg shadow-amber-500/25'
                      : !comparison
                      ? 'text-slate-600 cursor-not-allowed'
                      : 'text-slate-400 hover:text-white hover:bg-slate-700/50'
                  }`}
                >
                  <span className="flex items-center gap-2">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Histórico Completo
                  </span>
                </button>
                <button
                  onClick={() => setActiveTab('comparar')}
                  className={`px-6 py-2.5 rounded-lg font-medium transition-all duration-200 ${
                    activeTab === 'comparar'
                      ? 'bg-gradient-to-r from-purple-600 to-purple-500 text-white shadow-lg shadow-purple-500/25'
                      : 'text-slate-400 hover:text-white hover:bg-slate-700/50'
                  }`}
                >
                  <span className="flex items-center gap-2">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
                    </svg>
                    Comparar Times
                  </span>
                </button>
              </div>
            </div>

            {/* Vista Tática */}
            {activeTab === 'tatica' && comparison && (
              <>
                <div className="bg-slate-800/70 backdrop-blur-sm rounded-2xl p-6 border border-slate-700/50 card-hover">
                  <div className="flex items-center gap-4 mb-6">
                    <div className="relative">
                      <img
                        src={comparison.flag_url}
                        alt={comparison.team}
                        className="w-16 h-12 object-cover rounded-lg shadow-lg ring-2 ring-slate-600"
                      />
                      <div className="absolute -bottom-1 -right-1 w-5 h-5 bg-emerald-500 rounded-full flex items-center justify-center">
                        <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                        </svg>
                      </div>
                    </div>
                    <div>
                      <h2 className="text-2xl font-bold text-white">{comparison.team}</h2>
                      <p className="text-slate-400">
                        Referência: Copa {comparison.reference.season}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-slate-300 flex items-center gap-2">
                      <span className="w-1 h-6 bg-emerald-500 rounded-full"></span>
                      Similaridade com edicoes anteriores
                    </h3>

                    {/* Toggle de filtro */}
                    <label className="flex items-center gap-2 cursor-pointer">
                      <span className="text-sm text-slate-400">Apenas confiaveis</span>
                      <div className="relative">
                        <input
                          type="checkbox"
                          checked={showOnlyReliable}
                          onChange={(e) => setShowOnlyReliable(e.target.checked)}
                          className="sr-only peer"
                        />
                        <div className="w-10 h-5 bg-slate-600 rounded-full peer peer-checked:bg-emerald-500 transition-colors"></div>
                        <div className="absolute left-0.5 top-0.5 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-5"></div>
                      </div>
                    </label>
                  </div>

                  {comparison.comparisons.length === 0 ? (
                    <div className="text-center py-8 text-slate-500">
                      <svg className="w-12 h-12 mx-auto mb-3 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                      </svg>
                      Apenas uma edicao disponivel para esta selecao.
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {comparison.comparisons
                        .filter(comp => !showOnlyReliable || comp.confidence !== 'low')
                        .map((comp) => (
                          <SimilarityBar
                            key={comp.year}
                            year={comp.year}
                            similarity={comp.similarity}
                            confidence={comp.confidence}
                            featuresUsed={comp.features_used}
                            featuresMissing={comp.features_missing}
                            totalFeaturesUsed={comp.total_features_used}
                            source={comp.source}
                            nMatches={comp.n_matches}
                            totalMatches={comp.total_matches}
                          />
                        ))}
                    </div>
                  )}

                  {/* Legenda de confianca */}
                  <div className="mt-6 p-4 bg-slate-700/30 rounded-xl border border-slate-600/30">
                    <div className="flex flex-wrap gap-4 text-xs">
                      <div className="flex items-center gap-2">
                        <span className="w-3 h-3 rounded-full bg-emerald-500"></span>
                        <span className="text-slate-400">Alta (12 features)</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="w-3 h-3 rounded-full bg-amber-500"></span>
                        <span className="text-slate-400">Media (3-5 features)</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className="w-3 h-3 rounded-full bg-red-500"></span>
                        <span className="text-slate-400">Baixa (1-2 features)</span>
                      </div>
                    </div>
                    <p className="text-xs text-slate-500 mt-2">
                      Passe o mouse sobre uma barra para ver quais features foram usadas no calculo.
                    </p>
                  </div>
                </div>

                {comparison.reference.features && (
                  <TacticCard
                    title={`Perfil Tático - Copa ${comparison.reference.season}`}
                    features={comparison.reference.features}
                    featureNames={comparison.feature_names}
                  />
                )}
              </>
            )}

            {/* Vista Histórico */}
            {activeTab === 'historico' && history && (
              <div className="space-y-6">
                {/* Estatisticas gerais */}
                <div className="bg-gradient-to-br from-slate-800/90 to-slate-800/70 backdrop-blur-sm rounded-2xl p-6 border border-amber-500/20 glow-gold">
                  <div className="flex items-center gap-4 mb-6">
                    <div className="relative">
                      <img
                        src={history.flag_url}
                        alt={history.team}
                        className="w-20 h-14 object-cover rounded-lg shadow-xl ring-2 ring-amber-500/30"
                      />
                    </div>
                    <div>
                      <h2 className="text-3xl font-bold text-white">{history.team}</h2>
                      <p className="text-amber-400 font-medium flex items-center gap-2">
                        {history.estatisticas.titulos > 0 && (
                          <>
                            <span className="text-amber-400">
                              <TrophyIcon />
                            </span>
                            {history.estatisticas.titulos}x Campeão Mundial
                          </>
                        )}
                        {history.estatisticas.titulos === 0 && (
                          <span className="text-slate-400">{history.estatisticas.copas_disputadas} participações</span>
                        )}
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                    <div className="bg-gradient-to-br from-amber-500/20 to-amber-600/10 rounded-xl p-4 text-center border border-amber-500/20">
                      <div className="text-3xl font-bold text-amber-400">{history.estatisticas.titulos}</div>
                      <div className="text-xs text-amber-200/60 uppercase tracking-wide mt-1">títulos</div>
                    </div>
                    <div className="bg-slate-700/50 rounded-xl p-4 text-center border border-slate-600/30">
                      <div className="text-3xl font-bold text-white">{history.estatisticas.copas_disputadas}</div>
                      <div className="text-xs text-slate-400 uppercase tracking-wide mt-1">Copas</div>
                    </div>
                    <div className="bg-slate-700/50 rounded-xl p-4 text-center border border-slate-600/30">
                      <div className="text-3xl font-bold text-emerald-400">{history.estatisticas.total_gols}</div>
                      <div className="text-xs text-slate-400 uppercase tracking-wide mt-1">gols</div>
                    </div>
                    <div className="bg-slate-700/50 rounded-xl p-4 text-center border border-slate-600/30">
                      <div className="text-3xl font-bold text-blue-400">{history.estatisticas.total_jogos}</div>
                      <div className="text-xs text-slate-400 uppercase tracking-wide mt-1">jogos</div>
                    </div>
                  </div>

                  {/* Anos dos títulos */}
                  {history.estatisticas.anos_titulos.length > 0 && (
                    <div className="mb-6">
                      <div className="text-xs text-slate-500 uppercase tracking-wide mb-2">Anos dos títulos</div>
                      <div className="flex flex-wrap gap-2">
                        {history.estatisticas.anos_titulos.map(ano => (
                          <span key={ano} className="px-3 py-1.5 bg-amber-500/20 text-amber-300 rounded-lg text-sm font-medium border border-amber-500/30">
                            {ano}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Legenda de confiabilidade */}
                  <div className="flex flex-wrap gap-4 text-xs border-t border-slate-700/50 pt-4">
                    <div className="flex items-center gap-2">
                      <span className="w-3 h-3 rounded-full bg-emerald-500 shadow-lg shadow-emerald-500/50"></span>
                      <span className="text-slate-400">Completo ({history.cobertura.completo.length})</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="w-3 h-3 rounded-full bg-amber-500 shadow-lg shadow-amber-500/50"></span>
                      <span className="text-slate-400">Parcial ({history.cobertura.parcial.length})</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="w-3 h-3 rounded-full bg-slate-500"></span>
                      <span className="text-slate-400">Referência ({history.cobertura.referencia.length})</span>
                    </div>
                  </div>
                </div>

                {/* Cards por decada - mais recentes primeiro */}
                {[2020, 2010, 2000, 1990, 1980, 1970, 1960, 1950, 1940, 1930].map(decada => {
                  const copasDecada = history.copas.filter(
                    c => c.ano >= decada && c.ano < decada + 10
                  ).reverse()

                  if (copasDecada.length === 0) return null

                  return (
                    <div key={decada}>
                      <h3 className="text-sm font-semibold text-slate-500 mb-3 uppercase tracking-wider flex items-center gap-2">
                        <span className="w-8 h-px bg-slate-700"></span>
                        Anos {decada}
                        <span className="flex-1 h-px bg-slate-700"></span>
                      </h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {copasDecada.map(copa => (
                          <HistoryCard
                            key={copa.ano}
                            copa={copa}
                            flagUrl={history.flag_url}
                          />
                        ))}
                      </div>
                    </div>
                  )
                })}
              </div>
            )}

            {/* Vista Comparar Times */}
            {activeTab === 'comparar' && (
              <CrossCompare />
            )}

            {/* Prompt quando não há time selecionado (exceto na aba Comparar) */}
            {!comparison && activeTab !== 'comparar' && (
              <div className="text-center py-12">
                <div className="inline-flex flex-col items-center">
                  <div className="w-20 h-20 bg-slate-800/50 rounded-2xl flex items-center justify-center mb-4 border border-slate-700/50">
                    <svg className="w-10 h-10 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                    </svg>
                  </div>
                  <p className="text-slate-500 text-lg">Selecione uma seleção para ver sua herança tática</p>
                  <p className="text-slate-600 text-sm mt-2">
                    Ou use a aba <button onClick={() => setActiveTab('comparar')} className="text-purple-400 hover:text-purple-300 underline">Comparar Times</button> para comparações diretas
                  </p>
                </div>
              </div>
            )}
          </div>
        )}

        <footer className="mt-20 text-center border-t border-slate-800 pt-8">
          <div className="flex justify-center gap-8 mb-4">
            <div className="text-center">
              <div className="text-xs text-slate-600 uppercase tracking-wide">Dados Táticos</div>
              <div className="text-sm text-slate-400 mt-1">StatsBomb Open Data</div>
            </div>
            <div className="w-px h-10 bg-slate-800"></div>
            <div className="text-center">
              <div className="text-xs text-slate-600 uppercase tracking-wide">Dados Históricos</div>
              <div className="text-sm text-slate-400 mt-1">FIFA / Registros Oficiais</div>
            </div>
          </div>
          <div className="text-xs text-slate-700">
            Copas do Mundo 1930-2022 | Análise tática completa: 1970, 2018, 2022
          </div>
        </footer>
      </div>
    </div>
  )
}

export default App
