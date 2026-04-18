/**
 * badge.js — M7: Impact score → badge mapping utility
 *
 * Pure JS, no React imports. Used by ReportDetailPanel (M6)
 * and any other component that needs to display a citizen badge.
 *
 * getBadge(impactScore) → { tier, subBadge, tierLevel, color, bg, icon }
 */

export const TIER_NAMES = [
  'Unknown',
  'Rookie',
  'Community Hero',
  'Master Reformer',
  'StreetLight Paragon',
]

const TIER_STYLE = {
  1: { color: '#B45309', bg: '#FEF3C7', icon: '⭐' },
  2: { color: '#1D4ED8', bg: '#DBEAFE', icon: '🛡️' },
  3: { color: '#7C3AED', bg: '#F3E8FF', icon: '💎' },
  4: { color: '#15803D', bg: '#DCFCE7', icon: '🏆' },
}

const UNKNOWN = {
  tier:      'Unknown',
  subBadge:  'Unranked',
  tierLevel: 0,
  color:     '#6B7280',
  bg:        '#F3F4F6',
  icon:      '—',
}

// Ordered band definitions: [maxScore, tier, subBadge, tierLevel]
const BANDS = [
  [  66, 'Rookie',               'Street Scout',        1],
  [ 133, 'Rookie',               'Road Ranger',         1],
  [ 200, 'Rookie',               'Eagle Eye',           1],
  [ 300, 'Community Hero',       'Civic Warrior',       2],
  [ 400, 'Community Hero',       'Street Sentinel',     2],
  [ 500, 'Community Hero',       'Problem Buster',      2],
  [ 600, 'Master Reformer',      'Urban Legend',        3],
  [ 700, 'Master Reformer',      'Infrastructure Icon', 3],
  [ 800, 'Master Reformer',      'Trust Titan',         3],
  [ 866, 'StreetLight Paragon',  'City Architect',      4],
  [ 933, 'StreetLight Paragon',  'Beacon of Change',    4],
  [1000, 'StreetLight Paragon',  'Grand Overseer',      4],
]

/**
 * Map an impact_score to a full badge descriptor.
 *
 * @param {number|null|undefined} impactScore
 * @returns {{ tier, subBadge, tierLevel, color, bg, icon }}
 */
export function getBadge(impactScore) {
  if (impactScore == null || typeof impactScore !== 'number') return UNKNOWN

  const score = Math.max(0, Math.min(1000, impactScore))

  for (const [max, tier, subBadge, tierLevel] of BANDS) {
    if (score <= max) {
      return { tier, subBadge, tierLevel, ...TIER_STYLE[tierLevel] }
    }
  }

  // Fallback for any score > 1000 (shouldn't happen but be safe)
  return { tier: 'StreetLight Paragon', subBadge: 'Grand Overseer', tierLevel: 4, ...TIER_STYLE[4] }
}
