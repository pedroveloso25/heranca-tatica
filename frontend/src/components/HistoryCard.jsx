/**
 * Card para exibir Copa do Mundo com todos os níveis de confiabilidade
 * Visual refinado com tema de Copa
 */

const RESULTADO_CONFIG = {
  campeao: {
    text: 'Campeão',
    color: 'text-amber-300',
    bg: 'bg-gradient-to-r from-amber-500/30 to-amber-600/20',
    border: 'border-amber-500/40',
    icon: (
      <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
      </svg>
    )
  },
  vice: {
    text: 'Vice-campeao',
    color: 'text-slate-300',
    bg: 'bg-gradient-to-r from-slate-400/20 to-slate-500/10',
    border: 'border-slate-400/30',
    icon: (
      <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
      </svg>
    )
  },
  terceiro: {
    text: '3º lugar',
    color: 'text-amber-600',
    bg: 'bg-gradient-to-r from-amber-700/20 to-amber-800/10',
    border: 'border-amber-700/30',
    icon: null
  },
  semifinal: {
    text: 'Semifinal',
    color: 'text-blue-400',
    bg: 'bg-blue-500/10',
    border: 'border-blue-500/20',
    icon: null
  },
  quartas: {
    text: 'Quartas',
    color: 'text-emerald-400',
    bg: 'bg-emerald-500/10',
    border: 'border-emerald-500/20',
    icon: null
  },
  oitavas: {
    text: 'Oitavas',
    color: 'text-teal-400',
    bg: 'bg-teal-500/10',
    border: 'border-teal-500/20',
    icon: null
  },
  fase_grupos: {
    text: 'Fase de grupos',
    color: 'text-slate-500',
    bg: 'bg-slate-500/10',
    border: 'border-slate-500/20',
    icon: null
  },
}

// Indicador de nível de confiabilidade
function ConfidenceIndicator({ nivel }) {
  if (nivel === 'completo') {
    return (
      <div className="flex items-center gap-1 text-xs text-emerald-400" title="Dados táticos completos">
        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
        <span>Completo</span>
      </div>
    )
  }
  if (nivel === 'parcial') {
    return (
      <div className="flex items-center gap-1 text-xs text-amber-400" title="Dados táticos parciais">
        <span className="w-1.5 h-1.5 rounded-full bg-amber-500"></span>
        <span>Parcial</span>
      </div>
    )
  }
  return (
    <div className="flex items-center gap-1 text-xs text-slate-500" title="Apenas dados históricos">
      <span className="w-1.5 h-1.5 rounded-full bg-slate-600"></span>
      <span>Referência</span>
    </div>
  )
}

function HistoryCard({ copa, flagUrl }) {
  const config = RESULTADO_CONFIG[copa.resultado_final] || RESULTADO_CONFIG.fase_grupos
  const isCampeao = copa.resultado_final === 'campeao'

  return (
    <div className={`
      relative overflow-hidden rounded-xl p-4 card-hover
      ${isCampeao
        ? 'bg-gradient-to-br from-amber-900/30 via-slate-800/90 to-slate-800/70 border-2 border-amber-500/30 glow-gold'
        : 'bg-slate-800/60 border border-slate-700/50'
      }
    `}>
      {/* Fundo decorativo para campeões */}
      {isCampeao && (
        <div className="absolute top-0 right-0 w-24 h-24 bg-amber-500/10 rounded-full blur-2xl -translate-y-1/2 translate-x-1/2" />
      )}

      <div className="relative">
        {/* Header: Ano e Resultado */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            {flagUrl && (
              <img
                src={flagUrl}
                alt=""
                className={`w-8 h-6 object-cover rounded shadow ${isCampeao ? 'ring-1 ring-amber-500/50' : 'opacity-70'}`}
              />
            )}
            <div>
              <span className={`text-xl font-bold ${isCampeao ? 'text-amber-300' : 'text-white'}`}>
                Copa {copa.ano}
              </span>
              <ConfidenceIndicator nivel={copa.nivel_confiabilidade} />
            </div>
          </div>

          <div className={`
            flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium
            ${config.bg} ${config.border} border ${config.color}
          `}>
            {config.icon}
            {config.text}
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-3 gap-3">
          <div className={`rounded-lg p-3 text-center ${isCampeao ? 'bg-slate-800/50' : 'bg-slate-700/40'}`}>
            <div className="text-2xl font-bold text-white">{copa.jogos}</div>
            <div className="text-xs text-slate-500 mt-0.5">jogos</div>
          </div>
          <div className={`rounded-lg p-3 text-center ${isCampeao ? 'bg-slate-800/50' : 'bg-slate-700/40'}`}>
            <div className="text-2xl font-bold text-emerald-400">{copa.gols_marcados}</div>
            <div className="text-xs text-slate-500 mt-0.5">gols pro</div>
          </div>
          <div className={`rounded-lg p-3 text-center ${isCampeao ? 'bg-slate-800/50' : 'bg-slate-700/40'}`}>
            <div className="text-2xl font-bold text-red-400">{copa.gols_sofridos}</div>
            <div className="text-xs text-slate-500 mt-0.5">gols contra</div>
          </div>
        </div>

        {/* Saldo de gols */}
        <div className="mt-3 flex items-center justify-between text-sm">
          <span className="text-slate-500">Saldo de gols</span>
          <span className={`font-bold ${copa.saldo > 0 ? 'text-emerald-400' : copa.saldo < 0 ? 'text-red-400' : 'text-slate-400'}`}>
            {copa.saldo > 0 ? '+' : ''}{copa.saldo}
          </span>
        </div>

        {/* Aviso para dados de referência */}
        {copa.nivel_confiabilidade === 'referencia' && (
          <div className="mt-3 pt-3 border-t border-slate-700/50 text-xs text-slate-500 italic flex items-center gap-1.5">
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Dados táticos não disponíveis
          </div>
        )}
      </div>
    </div>
  )
}

export default HistoryCard
