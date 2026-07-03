const FEATURE_LABELS = {
  defensive_line_height: {
    name: 'Altura da Linha',
    description: 'Posição média da defesa (0-120)',
    format: (v) => `${v.toFixed(0)}m`,
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
      </svg>
    ),
    color: 'text-blue-400',
    bg: 'bg-blue-500/10',
  },
  ppda: {
    name: 'PPDA',
    description: 'Pressão alta (menor = mais intensa)',
    format: (v) => v.toFixed(1),
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
    ),
    color: 'text-amber-400',
    bg: 'bg-amber-500/10',
  },
  short_pass_pct: {
    name: 'Passes Curtos',
    description: 'Percentual de passes < 15m',
    format: (v) => `${(v * 100).toFixed(0)}%`,
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 15l-2 5L9 9l11 4-5 2zm0 0l5 5M7.188 2.239l.777 2.897M5.136 7.965l-2.898-.777M13.95 4.05l-2.122 2.122m-5.657 5.656l-2.12 2.122" />
      </svg>
    ),
    color: 'text-emerald-400',
    bg: 'bg-emerald-500/10',
  },
  long_pass_pct: {
    name: 'Passes Longos',
    description: 'Percentual de passes > 30m',
    format: (v) => `${(v * 100).toFixed(0)}%`,
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z" />
      </svg>
    ),
    color: 'text-orange-400',
    bg: 'bg-orange-500/10',
  },
  attack_width: {
    name: 'Largura Ofensiva',
    description: 'Dispersão lateral no ataque',
    format: (v) => `${v.toFixed(0)}m`,
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
      </svg>
    ),
    color: 'text-purple-400',
    bg: 'bg-purple-500/10',
  },
  transition_speed: {
    name: 'Velocidade de Transição',
    description: 'Progressão em 10s após recuperação',
    format: (v) => `${v.toFixed(0)}m`,
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
      </svg>
    ),
    color: 'text-cyan-400',
    bg: 'bg-cyan-500/10',
  },
  cross_vs_central: {
    name: 'Cruzamentos vs Central',
    description: 'Proporção de jogo pelas pontas',
    format: (v) => `${(v * 100).toFixed(0)}%`,
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
      </svg>
    ),
    color: 'text-pink-400',
    bg: 'bg-pink-500/10',
  },
  counterpress_rate: {
    name: 'Reação à Perda',
    description: 'Pressão imediata após perder bola',
    format: (v) => `${(v * 100).toFixed(0)}%`,
    icon: (
      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z" />
      </svg>
    ),
    color: 'text-red-400',
    bg: 'bg-red-500/10',
  },
}

function TacticCard({ title, features, featureNames }) {
  if (!features) return null

  return (
    <div className="bg-slate-800/70 backdrop-blur-sm rounded-2xl p-4 sm:p-6 border border-slate-700/50 card-hover">
      <h3 className="text-base sm:text-lg font-semibold text-white mb-4 sm:mb-5 flex items-center gap-2">
        <span className="w-1 h-5 sm:h-6 bg-emerald-500 rounded-full"></span>
        {title}
      </h3>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2 sm:gap-4">
        {featureNames.map((name) => {
          const info = FEATURE_LABELS[name] || {
            name: name,
            description: '',
            format: (v) => v?.toFixed(2) ?? '-',
            icon: (
              <svg className="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            ),
            color: 'text-slate-400',
            bg: 'bg-slate-500/10',
          }
          const value = features[name]

          // Pular features que não existem para este time
          if (value === undefined || value === null) return null

          // Função de formatação segura
          const safeFormat = (v) => {
            if (v === undefined || v === null) return '-'
            try {
              return info.format(v)
            } catch {
              return v.toString()
            }
          }

          return (
            <div
              key={name}
              className={`${info.bg} rounded-lg sm:rounded-xl p-2.5 sm:p-4 transition-all duration-200 active:scale-95 sm:hover:scale-105 border border-transparent hover:border-slate-600/30`}
            >
              <div className="flex items-center gap-1.5 sm:gap-2 mb-1 sm:mb-2">
                <span className={`${info.color} [&>svg]:w-4 [&>svg]:h-4 sm:[&>svg]:w-5 sm:[&>svg]:h-5`}>{info.icon}</span>
                <span className="text-slate-400 text-[10px] sm:text-xs uppercase tracking-wide font-medium truncate">
                  {info.name}
                </span>
              </div>
              <div className={`text-xl sm:text-3xl font-bold ${info.color}`}>
                {safeFormat(value)}
              </div>
              <div className="text-[10px] sm:text-xs text-slate-500 mt-1 sm:mt-2 leading-relaxed line-clamp-2">
                {info.description}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default TacticCard
