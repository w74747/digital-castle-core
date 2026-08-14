import React from 'react';
import { dcEntity, dcLegal } from '../tokens/tokens';
import { DigitalCastleLogo } from './DigitalCastleLogo';

type Lang = 'en' | 'ar';

/** Corporate header: logo left, document class eyebrow right, Castle Blue rule under. Mirrors in RTL. */
export function DocumentHeader({ classEn, classAr, lang = 'en' }:
  { classEn: string; classAr?: string; lang?: Lang }) {
  return (
    <header className="dc-doc-header" dir={lang === 'ar' ? 'rtl' : 'ltr'}>
      <DigitalCastleLogo cut="primary" />
      <div style={{ textAlign: lang === 'ar' ? 'left' : 'right', display: 'grid', gap: 5 }}>
        <span className="dc-eyebrow">{classEn}</span>
        {classAr && <span className="dc-eyebrow" dir="rtl">{classAr}</span>}
      </div>
    </header>
  );
}

/** Legal footer. Statutory on every official document — C.R., VAT, contact, page, confidentiality. */
export function DocumentFooter({ page, total, lang = 'en', confidential = true }:
  { page?: number; total?: number; lang?: Lang; confidential?: boolean }) {
  const ar = lang === 'ar';
  return (
    <footer dir={ar ? 'rtl' : 'ltr'}>
      <div className="dc-doc-footer">
        <span>{ar ? dcLegal.footerAr : `${dcLegal.footerEn} · VAT ${dcEntity.vatId}`}</span>
        <span dir="ltr">{dcEntity.website} · {dcEntity.email} · {dcEntity.phone}</span>
        {page != null && <span className="dc-meta">{page}{total ? ` / ${total}` : ''}</span>}
      </div>
      {confidential && (
        <div className="dc-confidential">{ar ? dcLegal.confidentialityAr : dcLegal.confidentialityEn}</div>
      )}
    </footer>
  );
}

/** One callout per section, maximum. It is read every time precisely because it is rare. */
export function Callout({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <aside className="dc-callout">
      <div className="dc-callout__title">{title}</div>
      <div>{children}</div>
    </aside>
  );
}

export function Kpi({ value, label }: { value: string; label: string }) {
  return (
    <div className="dc-kpi">
      <div className="dc-kpi__value">{value}</div>
      <div className="dc-kpi__label">{label}</div>
    </div>
  );
}

/** Hairline table. Numeric columns are mono + tabular + right-aligned, always. */
export function DataTable({ columns, rows }:
  { columns: { key: string; label: string; numeric?: boolean }[]; rows: Record<string, React.ReactNode>[] }) {
  return (
    <table className="dc-table">
      <thead>
        <tr>{columns.map(c => <th key={c.key} className={c.numeric ? 'dc-num' : undefined}>{c.label}</th>)}</tr>
      </thead>
      <tbody>
        {rows.map((r, i) => (
          <tr key={i}>{columns.map(c => <td key={c.key} className={c.numeric ? 'dc-num' : undefined}>{r[c.key]}</td>)}</tr>
        ))}
      </tbody>
    </table>
  );
}
