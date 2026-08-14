import React from 'react';

type Cut = 'primary' | 'reversed' | 'mark';
type Props = { cut?: Cut; height?: number; className?: string; href?: string };

/**
 * Digital Castle logo. The ONLY sanctioned way to render the mark.
 * Never recolour, rotate, outline, add effects to, or rebuild the artwork.
 * - primary  : full bilingual lock-up, dark wordmark. Light grounds.
 * - reversed : full bilingual lock-up, white wordmark. Dark grounds (--dc-keep / --dc-ink).
 * - mark     : cube only. Favicons, avatars, seals, tight headers. Min 40px.
 * Minimum lock-up size: 34mm print / 160px screen. Below that, use cut="mark".
 * Clear space: 1× the cube width on all four sides.
 */
export function DigitalCastleLogo({ cut = 'primary', height, className, href = '/brand/logo' }: Props) {
  const src = `${href}/digital-castle-${cut}.svg`;
  const h = height ?? (cut === 'mark' ? 40 : 46);
  return (
    <img
      src={src}
      alt="القلعة الرقمية ش.ش.و · Digital Castle S.P.C"
      height={h}
      style={{ height: h, width: 'auto', display: 'block' }}
      className={className}
    />
  );
}
