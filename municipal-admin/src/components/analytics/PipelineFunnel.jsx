// Module 2 — Pipeline stage funnel (true SVG trapezoids, count-based)
// Same trapezoid approach as PipelineLifecycleFunnel but shows counts per stage.

const CX         = 130
const Y_START    = 15
const LAYER_H    = 34
const GAP        = 4
const LINE_END_X = 375
const LABEL_X    = 383

// 6 stages — half-widths narrow from top to bottom
const LAYER_DEFS = [
  { halfTop: 100, halfBot: 84, color: '#94A3B8' },   // NEW
  { halfTop: 84,  halfBot: 68, color: '#60A5FA' },   // PENDING_VERIFICATION
  { halfTop: 68,  halfBot: 52, color: '#34D399' },   // VERIFIED
  { halfTop: 52,  halfBot: 36, color: '#F59E0B' },   // IN_PROGRESS
  { halfTop: 36,  halfBot: 20, color: '#FB923C' },   // AWAITING_FEEDBACK
  { halfTop: 20,  halfBot: 10, color: '#22C55E' },   // RESOLVED
]

function buildTrapezoidPoints(cxPx, halfTopPx, halfBottomPx, yTopPx, yBottomPx) {
  return [
    `${cxPx - halfTopPx},${yTopPx}`,
    `${cxPx + halfTopPx},${yTopPx}`,
    `${cxPx + halfBottomPx},${yBottomPx}`,
    `${cxPx - halfBottomPx},${yBottomPx}`,
  ].join(' ')
}

export default function PipelineFunnel({ stages, bottleneck, title }) {
  if (!stages?.length) return null

  const totalHeight = Y_START + stages.length * (LAYER_H + GAP) + 10

  return (
    <div>
      <p className="text-sm font-semibold text-gray-700 mb-2">{title}</p>
      <svg
        viewBox={`0 0 500 ${totalHeight}`}
        width="100%"
        role="img"
        aria-label="Report pipeline funnel by stage count"
        style={{ display: 'block' }}
      >
        {stages.map((stage, i) => {
          const def  = LAYER_DEFS[i]
          if (!def) return null

          const yTop = Y_START + i * (LAYER_H + GAP)
          const yBot = yTop + LAYER_H
          const yCtr = yTop + LAYER_H / 2

          const isBottleneck = stage.stage === bottleneck && stage.stage !== 'RESOLVED' && stage.count > 0
          const points       = buildTrapezoidPoints(CX, def.halfTop, def.halfBot, yTop, yBot)
          const lineStartX   = CX + def.halfTop + 8

          return (
            <g key={stage.stage}>
              {/* Trapezoid */}
              <polygon points={points} fill={def.color} />

              {/* Count label inside */}
              {stage.count > 0 && (
                <text
                  x={CX} y={yCtr}
                  textAnchor="middle"
                  dominantBaseline="middle"
                  fill="#FFFFFF"
                  fontSize={12}
                  fontWeight="bold"
                  fontFamily="Inter, Helvetica, sans-serif"
                >
                  {stage.count}
                </text>
              )}

              {/* Connector line */}
              <line
                x1={lineStartX} y1={yCtr}
                x2={LINE_END_X} y2={yCtr}
                stroke="#CBD5E1" strokeWidth={1}
              />

              {/* Stage label + bottleneck flag */}
              <text
                x={LABEL_X} y={yCtr}
                dominantBaseline="middle"
                fill="#374151"
                fontSize={11}
                fontFamily="Inter, Helvetica, sans-serif"
              >
                {stage.label}{isBottleneck ? ' ⚠' : ''}
              </text>
            </g>
          )
        })}
      </svg>
    </div>
  )
}
