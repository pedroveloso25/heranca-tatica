import { useState } from 'react'

function SimilarityBar({
  year,
  season, // compatibilidade
  similarity,
  confidence,
  featuresUsed = [],
  featuresMissing = [],
  totalFeaturesUsed,
  source,
  nMatches
}) {
  const [showTooltip, setShowTooltip] = useState(false)

  // Usar year ou season (compatibilidade)
  const displayYear = year || season

  // Similaridade já está em 0-1, converter para percentual
  const percentage = similarity * 100

  // Cores baseadas na similaridade
  const getColor = (sim) => {
    if (sim >= 0.8) return 'from-emerald-500 to-emerald-400'
    if (sim >= 0.6) return 'from-green-500 to-emerald-500'
    if (sim >= 0.4) return 'from-amber-500 to-yellow-500'
    if (sim >= 0.2) return 'from-orange-500 to-amber-500'
    return 'from-red-500 to-orange-500'
  }

  const getLabel = (sim) => {
    if (sim >= 0.8) return 'Muito similar'
    if (sim >= 0.6) return 'Similar'
    if (sim >= 0.4) return 'Moderado'
    if (sim >= 0.2) return 'Diferente'
    return 'Muito diferente'
  }

  const getLabelColor = (sim) => {
    if (sim >= 0.8) return 'text-emerald-400'
    if (sim >= 0.6) return 'text-green-400'
    if (sim >= 0.4) return 'text-amber-400'
    if (sim >= 0.2) return 'text-orange-400'
    return 'text-red-400'
  }

  // Estilos baseados na confiança
  const getConfidenceStyles = () => {
    switch (confidence) {
      case 'high':
        return {
          badge: null, // sem badge extra para high
          barClass: '',
          textClass: ''
        }
      case 'medium':
        return {
          badge: (
            <span className="flex items-center gap-1 text-amber-400 text-xs bg-amber-500/10 px-2 py-0.5 rounded-full">
              <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              {totalFeaturesUsed} features
            </span>
          ),
          barClass: 'opacity-80',
          textClass: ''
        }
      case 'low':
        return {
          badge: (
            <span className="flex items-center gap-1 text-red-400 text-xs bg-red-500/10 px-2 py-0.5 rounded-full">
              <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              Baixa confianca
            </span>
          ),
          barClass: 'opacity-60',
          textClass: 'text-red-400/70'
        }
      default:
        return { badge: null, barClass: '', textClass: '' }
    }
  }

  const styles = getConfidenceStyles()

  // Nomes amigáveis das features
  const featureNames = {
    defensive_line_height: 'Altura Linha',
    ppda: 'PPDA',
    short_pass_pct: 'Passes Curtos',
    long_pass_pct: 'Passes Longos',
    attack_width: 'Largura Ataque',
    transition_speed: 'Vel. Transicao',
    cross_vs_central: 'Cruzamentos',
    counterpress_rate: 'Reacao a Perda',
    posse: 'Posse',
    chutes_gol: 'Chutes a Gol',
    precisao_passes: 'Precisao Passes',
    xg: 'xG'
  }

  return (
    <div
      className="group py-2 relative"
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-3">
          <span className="text-white font-semibold text-lg">Copa {displayYear}</span>
          <span className="text-slate-500 text-sm bg-slate-700/50 px-2 py-0.5 rounded-full">
            {nMatches} jogos
          </span>
          {source && (
            <span className={`text-xs px-2 py-0.5 rounded-full ${
              source === 'statsbomb'
                ? 'bg-emerald-500/10 text-emerald-400'
                : 'bg-slate-600/50 text-slate-400'
            }`}>
              {source === 'statsbomb' ? 'Completo' : 'Historico'}
            </span>
          )}
          {styles.badge}
        </div>
        <div className="flex items-center gap-3">
          <span className={`text-sm font-medium ${getLabelColor(similarity)}`}>
            {getLabel(similarity)}
          </span>
          <span className="text-white font-bold text-lg tabular-nums">
            {percentage.toFixed(0)}%
          </span>
        </div>
      </div>

      <div className={`h-3 bg-slate-700/50 rounded-full overflow-hidden ${styles.barClass} ${
        confidence === 'low' ? 'border border-dashed border-red-500/30' : ''
      }`}>
        <div
          className={`h-full bg-gradient-to-r ${getColor(similarity)} transition-all duration-700 ease-out rounded-full relative`}
          style={{ width: `${Math.max(percentage, 5)}%` }}
        >
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
        </div>
      </div>

      {/* Aviso para low confidence */}
      {confidence === 'low' && (
        <div className="text-xs text-red-400/70 mt-1.5 flex items-center gap-1">
          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          Baixa confiabilidade - apenas {totalFeaturesUsed} features disponiveis
        </div>
      )}

      {/* Texto discreto para medium */}
      {confidence === 'medium' && (
        <div className="text-xs text-amber-400/60 mt-1.5 flex items-center gap-1">
          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Baseado em {totalFeaturesUsed} features. Dados taticos parciais.
        </div>
      )}

      {/* Tooltip com features */}
      {showTooltip && (featuresUsed.length > 0 || featuresMissing.length > 0) && (
        <div className="absolute left-0 right-0 top-full mt-2 z-50 bg-slate-800 border border-slate-600 rounded-xl p-4 shadow-xl">
          <div className="grid grid-cols-2 gap-x-6 gap-y-1 text-xs">
            {featuresUsed.map(f => (
              <div key={f} className="flex items-center gap-2 text-emerald-400">
                <span className="text-emerald-500">✓</span>
                {featureNames[f] || f}
              </div>
            ))}
            {featuresMissing.map(f => (
              <div key={f} className="flex items-center gap-2 text-slate-500">
                <span>—</span>
                {featureNames[f] || f}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default SimilarityBar
