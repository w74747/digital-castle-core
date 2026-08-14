/**
 * Digital Castle S.P.C — Tailwind preset
 * tailwind.config.js →  presets: [require('./brand-kit/tokens/tailwind.preset.js')]
 */
module.exports = {
  theme: {
    extend: {
      colors: {
        dc: {
          blue: '#0025FF', cyan: '#08F9F2', azure: '#0A7BF4',
          keep: '#071033', steel: '#2F4368',
          ink: '#0B1020', graphite: '#414C61', mist: '#6B7688', chalk: '#EAF0F7',
          paper: '#FFFFFF', canvas: '#F6F8FB', mesa: '#EDF1F7',
          frost: '#DCE2EC', 'frost-deep': '#C3CCDA',
          positive: '#0F7A5A', caution: '#B0731A', critical: '#C0342B',
        },
      },
      fontFamily: {
        display: ['Spectral', 'Georgia', 'serif'],
        sans: ['Plus Jakarta Sans', 'system-ui', 'sans-serif'],
        'display-ar': ['Almarai', 'Noto Kufi Arabic', 'sans-serif'],
        'sans-ar': ['IBM Plex Sans Arabic', 'Tahoma', 'sans-serif'],
        mono: ['IBM Plex Mono', 'ui-monospace', 'monospace'],
      },
      fontSize: {
        eyebrow: ['10px', { lineHeight: '1.2', letterSpacing: '.22em', fontWeight: '600' }],
        meta: ['11px', { lineHeight: '1.4', letterSpacing: '.06em' }],
        body: ['13px', { lineHeight: '1.62' }],
        lede: ['16px', { lineHeight: '1.55' }],
        h3: ['15px', { lineHeight: '1.3' }],
        h2: ['20px', { lineHeight: '1.25' }],
        h1: ['28px', { lineHeight: '1.18' }],
      },
      borderRadius: { DEFAULT: '0px', none: '0px' },
      backgroundImage: { 'dc-gradient': 'linear-gradient(135deg,#0025FF 0%,#08F9F2 100%)' },
      boxShadow: { doc: '0 18px 50px rgba(11,16,32,.16)' },
    },
  },
};
