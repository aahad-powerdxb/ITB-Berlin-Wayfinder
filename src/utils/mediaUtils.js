// Lightweight existence checks using HEAD requests instead of DOM elements.
// This avoids creating <video> / <img> nodes just to probe files and is much
// cheaper for the browser, especially for large videos.
const headExists = async (url) => {
  try {
    const res = await fetch(url, { method: "HEAD", cache: "no-store" });
    if (!res.ok) return false;

    const ct = res.headers.get("content-type") || "";
    // If server returns HTML (SPA fallback / index.html), treat as missing.
    if (/text\/html/i.test(ct)) return false;

    return true;
  } catch {
    // Network or HEAD not supported => treat as missing for now.
    return false;
  }
};

export const findAvailableMedia = async (folder) => {
  if (!folder) {
    return {
      hasVideo: false,
      videoType: null,
      hasStatic: false,
      staticType: null,
    };
  }

  // 1. Check video formats (mp4 preferred over mov)
  const [videoMp4, videoMov] = await Promise.all([
    headExists(`${folder}/video.mp4`),
    headExists(`${folder}/video.mov`),
  ]);

  if (videoMp4 || videoMov) {
    return {
      hasVideo: true,
      videoType: videoMp4 ? "mp4" : "mov",
      hasStatic: false,
      staticType: null,
    };
  }

  // 2. No video: check static images
  const [staticPng, staticJpg] = await Promise.all([
    headExists(`${folder}/static.png`),
    headExists(`${folder}/static.jpg`),
  ]);

  return {
    hasVideo: false,
    videoType: null,
    hasStatic: staticPng || staticJpg,
    staticType: staticPng ? "png" : staticJpg ? "jpg" : null,
  };
};

