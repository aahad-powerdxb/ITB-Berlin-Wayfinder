// MediaCache.js
// Singleton cache for detecting and preloading media files under /media/<folder>
// Note: do not encode paths here; use raw sanitized folder paths that match the public/media folder names

export class MediaCache {
  constructor() {
    this.cache = new Map();
    this.queue = [];
    this.processing = false;
    // New: Queue management for active fetches
                    this.fetchQueue = new Map(); // url -> { controller, promise }
    // Lower concurrency to leave room for the main video player and critical assets
    this.MAX_CONCURRENT_FETCHES = 2;
  }


  // Cancel all active preloads
  cancelAll() {
    this.fetchQueue.forEach((fetchObj, url) => {
      fetchObj.controller.abort();
      console.log(`[MediaCache] Cancelled: ${url.split('/').pop()}`);
    });
    this.fetchQueue.clear();
  }





  get(folder) {
    return this.cache.get(folder);
  }

  set(folder, info) {
    this.cache.set(folder, info);
  }

  has(folder) {
    return this.cache.has(folder);
  }

    // Check existence using HEAD; fallback to Image preload for images
  async checkFile(url) {
    // Add a timeout to prevent hanging on stalled connections
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 2000); // 2 second timeout

    try {
      const res = await fetch(url, { method: 'HEAD', signal: controller.signal });
      clearTimeout(timeoutId);
      
      if (!res.ok) {
        return false;
      }

      const contentType = (res.headers && res.headers.get('content-type')) || '';
      
      // If server returns an HTML page (SPA fallback), treat as missing
      if (/text\/html/i.test(contentType)) {
        // Try a small-range GET for binary verification (useful when HEAD routes to index.html)
        try {
          const rangeRes = await fetch(url, { method: 'GET', headers: { Range: 'bytes=0-1023' } });
          if (!rangeRes.ok) {
            return false;
          }
          const rangeCt = (rangeRes.headers && rangeRes.headers.get('content-type')) || '';
          if (/text\/html/i.test(rangeCt)) {
            return false;
          }
          return /^(image|video)\//i.test(rangeCt) || /application\/octet-stream/i.test(rangeCt);
        } catch (err) {
          return false;
        }
      }
      // Accept images, videos, or generic binary responses
      if (/^(image|video)\//i.test(contentType) || /application\/octet-stream/i.test(contentType)) return true;
      // Unknown content-type but ok; allow as a last resort
      return true;
    } catch (err) {
      // If HEAD blocked, use image load check for images
      if (/\.(png|jpg|jpeg|gif)$/i.test(url)) {
        return new Promise((resolve) => {
          const img = new Image();
          img.onload = () => resolve(true);
          img.onerror = () => resolve(false);
          img.src = url;
        });
      }
      // For non-image resources, try a small-range GET as a fallback to verify resource is binary/video
      try {
        const rangeRes = await fetch(url, { method: 'GET', headers: { Range: 'bytes=0-1023' } });
        if (!rangeRes.ok) return false;
        const rangeCt = (rangeRes.headers && rangeRes.headers.get('content-type')) || '';
        if (/text\/html/i.test(rangeCt)) return false;
        return /^(image|video)\//i.test(rangeCt) || /application\/octet-stream/i.test(rangeCt);
      } catch (err2) {
        return false;
      }
    }
  }

        // Preload content using fetch (GET) with concurrency limit
  async preloadContent(url) {
    if (!url) return;

    // Check if already cached (memory or browser cache)
    if (this.fetchQueue.has(url)) return; // Already fetching

    // Reserve slot immediately to prevent race conditions
    const controller = new AbortController();
    const fetchObj = { controller, promise: null };
    this.fetchQueue.set(url, fetchObj);
    
    console.log(`[MediaCache] Requesting: ${url.split('/').pop()} (Queue: ${this.fetchQueue.size})`);

    try {
      const cached = await caches.match(url);
      if (cached) {
        this.fetchQueue.delete(url);
        return; // Already in HTTP cache
      }
    } catch (e) { /* ignore */ }

    // Manage concurrency: if queue is full, abort the oldest fetch
    // Since we just added ourselves, size > MAX means we need to remove someone else
    if (this.fetchQueue.size > this.MAX_CONCURRENT_FETCHES) {
      // Get the first key (oldest entry)
      const iterator = this.fetchQueue.keys();
      let oldestUrl = iterator.next().value;
      
      // Ensure we don't abort ourselves if we are the only one (unlikely given logic)
      if (oldestUrl === url) {
        oldestUrl = iterator.next().value;
      }

      if (oldestUrl) {
        const oldestFetch = this.fetchQueue.get(oldestUrl);
        if (oldestFetch) {
            console.log(`[MediaCache] Aborting: ${oldestUrl.split('/').pop()}`);
            oldestFetch.controller.abort();
            this.fetchQueue.delete(oldestUrl);
        }
      }
    }

    const signal = controller.signal;

    const fetchPromise = (async () => {
      try {
        const response = await fetch(url, { signal });
        if (response.ok) {
          const cache = await caches.open('media-cache-v1');
          await cache.put(url, response.clone());
          console.log(`[MediaCache] Cached: ${url.split('/').pop()}`);
        }
      } catch (err) {
        // Ignore AbortError, log others if needed
        if (err.name !== 'AbortError') {
          console.warn(`[MediaCache] Error ${url.split('/').pop()}:`, err);
        }
      } finally {
        // Remove from queue when done (success or fail)
        if (this.fetchQueue.get(url) === fetchObj) {
          this.fetchQueue.delete(url);
        }
      }
    })();

    fetchObj.promise = fetchPromise;
  }



  // Preload and detect media info for a folder
  // Returns an object: { type: 'video'|'static'|null, formats: { webm, mp4, mov }, format: 'png'|'jpg'|null, thumbnail: boolean }
  async preloadMedia(folder) {
    if (!folder) {
      return null;
    }
    if (this.has(folder)) {
      return this.get(folder);
    }

    const info = {
      type: null,
      formats: { webm: false, mp4: false, mov: false },
      format: null,
      thumbnail: false,
      error: null,
    };

        try {
      // Check video formats - PRIORITIZE MP4 as it is the standard
      // We check sequentially to avoid flooding the network with 3 simultaneous HEAD requests
      const mp4 = await this.checkFile(`${folder}/video.mp4`);
      
      // If MP4 exists, stop looking! We found our primary video.
      if (mp4) {
         info.type = 'video';
         info.formats = { webm: false, mp4: true, mov: false };
         info.thumbnail = await this.checkFile(`${folder}/video.jpg`);
      } else {
          // Only check others if MP4 is missing
          const webm = await this.checkFile(`${folder}/video.webm`);
          if (webm) {
             info.type = 'video';
             info.formats = { webm: true, mp4: false, mov: false };
             info.thumbnail = await this.checkFile(`${folder}/video.jpg`);
          } else {
             const mov = await this.checkFile(`${folder}/video.mov`);
             if (mov) {
                info.type = 'video';
                info.formats = { webm: false, mp4: false, mov: true };
                info.thumbnail = await this.checkFile(`${folder}/video.jpg`);
             }
          }
      }

      if (info.type === 'video') {
        // We already set info inside the logic above
      } else {
        // No video: check static images
        const png = await this.checkFile(`${folder}/static.png`);
        const jpg = await this.checkFile(`${folder}/static.jpg`);
        if (png || jpg) {
          info.type = 'static';
          info.format = png ? 'png' : 'jpg';
        }
      }

      this.set(folder, info);
      return info;
    } catch (err) {
      info.error = err && err.message ? err.message : String(err);
      this.set(folder, info);
      return info;
    }
  }

  // Queue a preload (simple FIFO)
  queuePreload(folder) {
    if (!folder || this.has(folder)) {
      return;
    }
    this.queue.push(folder);
    this._processQueue();
  }

  async _processQueue() {
    if (this.processing) {
      return;
    }

    this.processing = true;
    while (this.queue.length > 0) {
      const folder = this.queue.shift();
      try {
        await this.preloadMedia(folder);
      } catch (err) {
        // ignore per-folder failures but log them
        console.error('MediaCache preload error for', folder, err);
      }
    }
    this.processing = false;
  }
}

const mediaCache = new MediaCache();

export { mediaCache };


