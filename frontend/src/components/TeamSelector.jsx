// Seleções com dados táticos completos (StatsBomb >= 3 jogos)
const TEAMS_COMPLETO = [
  'Brazil', 'Germany', 'Argentina', 'France', 'England',
  'Spain', 'Netherlands', 'Uruguay', 'Italy', 'Belgium',
  'Croatia', 'Portugal', 'Mexico'
]

// Seleções com dados parciais (StatsBomb 1-2 jogos)
const TEAMS_PARCIAL = []

// Função para determinar nível de dados de uma seleção
function getDataLevel(teamName) {
  if (TEAMS_COMPLETO.includes(teamName)) return 'completo'
  if (TEAMS_PARCIAL.includes(teamName)) return 'parcial'
  return 'referencia'
}

// Ordenar times: completo > parcial > referencia, depois alfabético
function sortTeams(teams) {
  const levelOrder = { completo: 0, parcial: 1, referencia: 2 }

  return [...teams].sort((a, b) => {
    const levelA = getDataLevel(a.name)
    const levelB = getDataLevel(b.name)

    if (levelOrder[levelA] !== levelOrder[levelB]) {
      return levelOrder[levelA] - levelOrder[levelB]
    }

    return a.name.localeCompare(b.name)
  })
}

// Indicador de nivel de dados
function DataIndicator({ level }) {
  if (level === 'completo') {
    return (
      <span
        className="w-2 h-2 rounded-full bg-emerald-500 shadow-sm shadow-emerald-500/50"
        title="Dados táticos completos"
      />
    )
  }
  if (level === 'parcial') {
    return (
      <span
        className="w-2 h-2 rounded-full bg-amber-500 shadow-sm shadow-amber-500/50"
        title="Dados táticos parciais"
      />
    )
  }
  return null
}

function TeamSelector({ teams, selectedTeam, onSelect }) {
  const sortedTeams = sortTeams(teams)

  // Times para chips rápidos (top 8 com mais dados)
  const quickSelectTeams = sortedTeams
    .filter(t => t.name !== selectedTeam)
    .slice(0, 8)

  return (
    <div className="bg-slate-800/70 backdrop-blur-sm rounded-2xl p-6 border border-slate-700/50">
      <label className="block text-slate-300 font-medium mb-3 flex items-center gap-2">
        <svg className="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9" />
        </svg>
        Escolha uma seleção
      </label>

      <div className="relative">
        <select
          value={selectedTeam || ''}
          onChange={(e) => onSelect(e.target.value || null)}
          className="w-full bg-slate-700/80 text-white px-4 py-3.5 pr-10 rounded-xl
                     border border-slate-600/50 focus:border-emerald-500 focus:ring-2
                     focus:ring-emerald-500/20 outline-none appearance-none cursor-pointer
                     transition-all duration-200 hover:bg-slate-700"
        >
          <option value="">Selecione uma seleção...</option>

          {/* Grupo: Dados Completos */}
          <optgroup label="Dados Táticos Completos">
            {sortedTeams
              .filter(t => getDataLevel(t.name) === 'completo')
              .map((team) => (
                <option key={team.name} value={team.name}>
                  {team.name}
                </option>
              ))}
          </optgroup>

          {/* Grupo: Dados Parciais */}
          {sortedTeams.some(t => getDataLevel(t.name) === 'parcial') && (
            <optgroup label="Dados Táticos Parciais">
              {sortedTeams
                .filter(t => getDataLevel(t.name) === 'parcial')
                .map((team) => (
                  <option key={team.name} value={team.name}>
                    {team.name}
                  </option>
                ))}
            </optgroup>
          )}

          {/* Grupo: Apenas Referência */}
          {sortedTeams.some(t => getDataLevel(t.name) === 'referencia') && (
            <optgroup label="Apenas Dados Históricos">
              {sortedTeams
                .filter(t => getDataLevel(t.name) === 'referencia')
                .map((team) => (
                  <option key={team.name} value={team.name}>
                    {team.name}
                  </option>
                ))}
            </optgroup>
          )}
        </select>

        <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
          <svg className="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
      </div>

      {/* Chips de seleção rápida */}
      {teams.length > 0 && (
        <div className="mt-5">
          <div className="text-xs text-slate-500 uppercase tracking-wide mb-2">
            Seleção rápida
          </div>
          <div className="flex flex-wrap gap-2">
            {quickSelectTeams.map((team) => {
              const level = getDataLevel(team.name)
              const isSelected = team.name === selectedTeam

              return (
                <button
                  key={team.name}
                  onClick={() => onSelect(team.name)}
                  className={`flex items-center gap-2 px-3 py-2 rounded-xl text-sm
                             transition-all duration-200 group
                             ${isSelected
                               ? 'bg-emerald-600 text-white ring-2 ring-emerald-500/50'
                               : 'bg-slate-700/70 hover:bg-slate-600 text-slate-300 hover:text-white border border-slate-600/30 hover:border-slate-500/50'
                             }`}
                >
                  <img
                    src={team.flag_url}
                    alt={team.name}
                    className="w-6 h-4 object-cover rounded shadow-sm"
                  />
                  <span className="font-medium">{team.name}</span>
                  <DataIndicator level={level} />
                </button>
              )
            })}
          </div>
        </div>
      )}

      {/* Legenda dos indicadores */}
      <div className="mt-4 pt-4 border-t border-slate-700/50 flex flex-wrap gap-4 text-xs text-slate-500">
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
          <span>Tática completa</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-amber-500"></span>
          <span>Tática parcial</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-slate-600"></span>
          <span>Apenas histórico</span>
        </div>
      </div>
    </div>
  )
}

export default TeamSelector
