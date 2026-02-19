// urlUtils.js
// Encode folder path and filename for safe URL usage. Encode each path segment separately.
export function encodeMediaPath(folder, filename) {
  if (!folder) return '';
  const segments = folder.split('/').filter(Boolean);
  // Encode each segment, but restore common characters that sometimes
  // cause static file resolution issues on some dev servers (keep '&')
  const encodedPath = segments
    .map(s => encodeURIComponent(s).replace(/%26/g, '&'))
    .join('/');
  return `/${encodedPath}/${encodeURIComponent(filename)}`;
}