// ── Design tokens ─────────────────────────────────────────────────────────────
export const C = {
  primary:      '#B85C2E',
  primaryDark:  '#9C4C24',
  primaryLight: '#FFF3EB',
  pageBg:       '#F7F6E8',
  cardBg:       '#FFFFFF',
  mutedBg:      '#FDFCF0',
  border:       '#EDE8DC',
  text:         '#1A1208',
  textSub:      '#6B7280',
  textMuted:    '#9CA3AF',
}

// ── Kanban stage → { label, dot, bg, text } ───────────────────────────────────
export const STAGE_MAP = {
  NEW:                  { label: 'New',                 dot: '#6B7280', bg: '#F3F4F6', text: '#374151' },
  PENDING_VERIFICATION: { label: 'Pending Verification',dot: '#3B82F6', bg: '#EFF6FF', text: '#1D4ED8' },
  VERIFIED:             { label: 'Verified',            dot: '#F97316', bg: '#FFF7ED', text: '#C2410C' },
  IN_PROGRESS:          { label: 'In Progress',         dot: '#F59E0B', bg: '#FFFBEB', text: '#B45309' },
  AWAITING_FEEDBACK:    { label: 'Awaiting Feedback',   dot: '#8B5CF6', bg: '#F5F3FF', text: '#6D28D9' },
  RESOLVED:             { label: 'Resolved',            dot: '#22C55E', bg: '#F0FDF4', text: '#15803D' },
  CLOSED:               { label: 'Closed',              dot: '#64748B', bg: '#F1F5F9', text: '#475569' },
}

// ── Severity → { bg, text } ───────────────────────────────────────────────────
export const SEVERITY_MAP = {
  large:  { bg: '#FEF2F2', text: '#EF4444', label: 'High'   },
  medium: { bg: '#FFF7ED', text: '#F97316', label: 'Medium' },
  small:  { bg: '#F0FDF4', text: '#22C55E', label: 'Low'    },
  high:   { bg: '#FEF2F2', text: '#EF4444', label: 'High'   },
  low:    { bg: '#F0FDF4', text: '#22C55E', label: 'Low'    },
}

// ── Category → lucide icon name ───────────────────────────────────────────────
export const CATEGORY_ICON = {
  POTHOLE: 'AlertTriangle',
  TRASH:   'Trash2',
  GARBAGE: 'Trash2',
  default: 'ClipboardList',
}

// ── Role labels ───────────────────────────────────────────────────────────────
export const ROLE_LABEL = {
  super_admin:  'Super Admin',
  city_admin:   'City Admin',
  dept_officer: 'Dept. Officer',
}

// ── Dept full names ───────────────────────────────────────────────────────────
export const DEPT_LABEL = {
  lmc:  'Lahore Metropolitan Corporation',
  lwmc: 'Lahore Waste Management Company',
  fmc:  'Faisalabad Metropolitan Corporation',
  fwmc: 'Faisalabad Waste Management Company',
}
