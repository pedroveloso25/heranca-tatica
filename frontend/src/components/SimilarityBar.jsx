function SimilarityBar({ season, similarity, nMatches, nivelConfiabilidade, aviso }) {
  // Normalizar similaridade de [-1, 1] para [0, 100]
  const percentage = ((similarity + 1) / 2) * 100

  // Detectar se é dados parciais (menos de 3 jogos)
  const isParcial = nivelConfiabilidade === 'parcial' || nMatches < 3

  // Cor baseada na similaridade
  const getColor = (sim) => {
    if (sim >= 0.5) return 'from-emerald-500 to-emerald-400'
    if (sim >= 0.2) return 'from-green-500 to-emerald-500'
    if (sim >= 0) return 'from-amber-500 to-yellow-500'
    if (sim >= -0.3) return 'from-orange-500 to-amber-500'
    return 'from-red-500 to-orange-500'
  }

  const getLabel = (sim) => {
    if (sim >= 0.5) return 'Muito similar'
    if (sim >= 0.2) return 'Similar'
    if (sim >= 0) return 'Moderado'
    if (sim >= -0.3) return 'Diferente'
    return 'Muito diferente'
  }

  const getLabelColor = (sim) => {
    if (sim >= 0.5) return 'text-emerald-400'
    if (sim >= 0.2) return 'text-green-400'
    if (sim >= 0) return 'text-amber-400'
    if (sim >= -0.3) return 'text-orange-400'
    return 'text-red-400'
  }

  return (
    <div className="group py-2">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-3">
          <span className="text-white font-semibold text-lg">Copa {season}</span>
          <span className="text-slate-500 text-sm bg-slate-700/50 px-2 py-0.5 rounded-full">
            {nMatches} jogos
          </span>
          {isParcial && (
            <span
              className="flex items-center gap-1 text-amber-500 text-xs bg-amber-500/10 px-2 py-0.5 rounded-full cursor-help"
              title={aviso || `Baseado em ${nMatches} jogo(s). Baixa confiabilidade estatistica.`}
            >
              <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              Parcial
            </span>
          )}
        </div>
        <div className="flex items-center gap-3">
          <span className={`text-sm font-medium ${getLabelColor(similarity)}`}>
            {getLabel(similarity)}
          </span>
          <span className="text-white font-bold text-lg tabular-nums">
            {(similarity * 100).toFixed(0)}%
          </span>
        </div>
      </div>

      <div className={`h-3 bg-slate-700/50 rounded-full overflow-hidden ${isParcial ? 'opacity-70' : ''}`}>
        <div
          className={`h-full bg-gradient-to-r ${getColor(similarity)} transition-all duration-700 ease-out rounded-full relative`}
          style={{ width: `${Math.max(percentage, 5)}%` }}
        >
          {/* Brilho animado */}
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
        </div>
      </div>

      {isParcial && (
        <div className="text-xs text-amber-500/70 mt-1.5 flex items-center gap-1">
          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Dados limitados - baixa confiabilidade estatística
        </div>
      )}
    </div>
  )
}

export default SimilarityBar
