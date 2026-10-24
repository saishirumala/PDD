/**
 * Utility functions to parse and format timestamps accurately across timezones.
 * Backend stores timestamps in UTC (from SQLite/Postgres).
 * If a timestamp lacks explicit timezone info (e.g. "2026-10-23 15:15:23"),
 * this appends 'Z' so the browser parses it as UTC rather than local time.
 */

export function parseDate(dateStr?: string | null): Date {
  if (!dateStr) return new Date();
  let s = String(dateStr).trim();
  if (!s) return new Date();

  // If already ends with Z or has timezone offset like +05:30, -04:00, +0530, etc.
  if (!s.endsWith('Z') && !/[+-]\d{2}(:?\d{2})?$/.test(s)) {
    s = s.replace(' ', 'T') + 'Z';
  }

  const parsed = new Date(s);
  return isNaN(parsed.getTime()) ? new Date(dateStr) : parsed;
}

export function formatTime(dateStr?: string | null): string {
  try {
    const d = parseDate(dateStr);
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  } catch {
    return "";
  }
}

export function formatDate(
  dateStr?: string | null,
  options: Intl.DateTimeFormatOptions = { month: 'short', day: 'numeric', year: 'numeric' }
): string {
  try {
    const d = parseDate(dateStr);
    return d.toLocaleDateString([], options);
  } catch {
    return "";
  }
}

export function formatLongDate(dateStr?: string | null): string {
  try {
    const d = parseDate(dateStr);
    return d.toLocaleDateString([], { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
  } catch {
    return "";
  }
}
