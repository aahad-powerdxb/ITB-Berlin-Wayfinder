import React, { useEffect, useState, useRef } from 'react';
import { mediaCache } from '../utils/MediaCache';

// MediaViewer: given a `folder` (e.g. '/media/Name'), detect media and render either a video or an image.
// Props:
// - folder: string (required)
// - className / style: optional
// - onLoaded(info): optional callback with detected media info
// - placeholder: optional React node to render while detecting
export default function MediaViewer({ folder, className, style, onLoaded, placeholder = null }) {
  const [info, setInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const videoRef = useRef(null);
  
    useEffect(() => {
    let mounted = true;
    setInfo(null);
    setLoading(true);

    if (!folder) {
      console.log(`[MediaViewer] No folder provided.`);
      setLoading(false);
      return;
    }

    console.log(`[MediaViewer] Mount/Update: ${folder}`);

    (async () => {
      try {
        // Use cache if available
        let cached = mediaCache.get(folder);
        if (cached) {
            console.log(`[MediaViewer] Cache HIT for ${folder}`, cached);
        } else {
            console.log(`[MediaViewer] Cache MISS for ${folder}, preloading...`);
            cached = await mediaCache.preloadMedia(folder);
            console.log(`[MediaViewer] Preload result for ${folder}:`, cached);
        }
        
        if (!mounted) {
            console.log(`[MediaViewer] Unmounted during load for ${folder}`);
            return;
        }
        
        setInfo(cached);
        setLoading(false);
        if (onLoaded) onLoaded(cached);
      } catch (err) {
        console.error(`[MediaViewer] Error loading ${folder}:`, err);
        if (!mounted) return;
        setInfo({ error: err && err.message ? err.message : String(err) });
        setLoading(false);
        if (onLoaded) onLoaded({ error: err && err.message ? err.message : String(err) });
      }
    })();

        return () => {
      console.log(`[MediaViewer] Cleanup/Unmount: ${folder}`);
      mounted = false;
      if (videoRef.current) {
        try { 
          videoRef.current.pause(); 
        } catch (e) {
          // ignore error if component is already gone
        }
      }
    };
  }, [folder, onLoaded]);

  if (loading) return placeholder || <div className={className} style={style}>Loading…</div>;
  
  // Guard clause: If folder is empty, do not render anything, even if info is stale
  if (!folder) return null;

  if (!info || info.error || info.type === null) return null;

    if (info.type === 'video') {
    // choose ordering: webm, mp4, mov
    return (
      <video
        key={folder} // Force remount on folder change
        ref={videoRef}
        autoPlay
        loop
        muted
        playsInline
        className={className}
        style={style}
        poster={info.thumbnail ? `${folder}/video.jpg` : undefined}
                onError={(e) => {
            console.error(`[MediaViewer] Video playback error for ${folder}:`, e.nativeEvent);
            // Fallback: If video fails, force a reload with cache busting if not already tried
            if (!e.target.src.includes('?retry')) {
                // This is hard with <source> tags. We might need to force a re-render.
            }
        }}
        onCanPlay={(e) => {
            console.log(`[MediaViewer] CanPlay fired for ${folder}`);
            e.target.play().catch(err => console.error("[MediaViewer] Play failed:", err));
        }}
      >
                {info.formats.webm && <source src={`${folder}/video.webm`} type="video/webm" />}
        {info.formats.mp4 && <source src={`${folder}/video.mp4`} type="video/mp4" />}
        {info.formats.mov && <source src={`${folder}/video.mov`} type="video/quicktime" />}
        {/* If browser doesn't play video, nothing will show; fallback should be handled by parent if desired. */}
      </video>
    );
  }

  if (info.type === 'static') {
    // static image
    return (
      <img
        className={className}
        style={style}
        src={`${folder}/static.${info.format}`}
        alt=""
        loading="lazy"
        onError={(e) => {
          // final fallback: try the other extension
          const cur = e.target.getAttribute('src') || '';
          if (/\.png$/i.test(cur)) e.target.src = cur.replace(/\.png$/i, '.jpg');
          else if (/\.jpg$/i.test(cur)) e.target.src = cur.replace(/\.jpg$/i, '.png');
          else e.target.style.display = 'none';
        }}
      />
    );
  }

  return null;
}
