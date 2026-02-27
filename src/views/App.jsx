import React, { useEffect, useState } from "react";
import { useStateContext } from "../context/StateContext";
import { useSessionPersistence } from "../hooks/useSessionPersistence";
// Player animation removed — blink feature no longer used

import "../css/index.css";
import layoutStyles from "../css/AppLayout.module.css";
import {
  mapConfig,
  transitionConfig,
  mediaConfig,
  assetPaths,
  layoutConfig,
} from "../config/config.js";
import { mediaCache } from "../utils/MediaCache.js";
import { useMediaQuery } from "../hooks/useMediaQuery";
import MapView from "./MapView";
import DirectoryView from "./DirectoryView";
import DetailView from "./DetailView";
import MediaViewer from "../components/MediaViewer";

function App() {
  const { state, dispatch } = useStateContext();
  const { selectedData, eventData, currentMap, mediaState } = state;
  const [isContentVisible, setIsContentVisible] = useState(false); // 1. New state for visibility
  const isPortrait = useMediaQuery("(orientation: portrait)");
  useSessionPersistence();

  // Calculate layout variables
  const rightMapWidth = layoutConfig.rightMapWidthVW;
  const leftMapWidth = layoutConfig.leftMapWidthVW;
  const mapGap = layoutConfig.mapGapVW;
  const mapRightMargin = layoutConfig.mapRightMarginVW;
  const contentRightMargin = layoutConfig.contentRightMarginVW;

  // The total width occupied by the map system
  const totalMapWidth = rightMapWidth + leftMapWidth + mapGap + mapRightMargin;

  // The content width is the remaining space, minus the gap between content and map
  const contentWidth = 100 - totalMapWidth - contentRightMargin;

 // Get the default map for initial render
 const defaultFolder = `${mapConfig.mapsRootPath}${mapConfig.defaultFolder}`;
 
  useEffect(() => {
    // Initial fade-in for the directory view on component mount
    setIsContentVisible(true);
    dispatch({ type: "SET_CURRENT_MAP", payload: defaultFolder });
  }, [defaultFolder, dispatch]);

  // NOTE: we intentionally do not encode folder paths. The folder variable
  // represents the sanitized directory name inside `public/media` and should
  // be used as-is when building URLs so the dev server matches filesystem names.

  // Cleanup utility: pause and fully release any existing <video> elements so the browser
  // can free decoders and memory. Call this before mounting new videos or when leaving a view.
  function cleanupAllVideos() {
    try {
      document.querySelectorAll("video").forEach((v) => {
        try {
          v.pause();
        } catch (e) {}
        try {
          // Remove src so UA can drop internal buffers
          v.removeAttribute("src");
        } catch (e) {}
        try {
          // If used, clear any MediaStream
          if ("srcObject" in v) v.srcObject = null;
        } catch (e) {}
        try {
          // Instruct the element to reset
          v.load();
        } catch (e) {}
      });
    } catch (err) {
      // swallow errors - cleanup is best-effort
    }
  }

  function handleClick(data) {
    if (!data.inactive) {
      // Cancel any ongoing directory preloads to focus on detail view
      mediaCache.cancelAll();
      
      // Handle split IDs (e.g., "123_split_0") -> "123"
      const originalId = String(data.id).split('_split_')[0];

      setIsContentVisible(false); // Fade out content
      // Dispatch map change immediately to start map transition in parallel
      dispatch({
        type: "SET_CURRENT_MAP",
        payload: `${mapConfig.mapsRootPath}${data.booth}`,
      });
      setTimeout(() => {
        cleanupAllVideos();
        dispatch({ type: "SET_EVENT_DATA", payload: data });
        dispatch({ type: "SET_SELECTED_DATA", payload: true });
        dispatch({
          type: "SET_MEDIA_STATE",
          payload: {
            folder: `${mediaConfig.mediaRootPath}${originalId}`,
            hasVideo: false,
            videoType: null,
            hasStatic: false,
            staticType: null,
          },
        });
        
        // Trigger fade-in after a brief delay to ensure DOM update happens while hidden
        setTimeout(() => {
          setIsContentVisible(true); 
        }, 50);
        
      }, transitionConfig.contentFadeOutMS); // Match CSS transition duration
    }
  }

  function handleBackClick() {
    // Cancel any detail view preloads (if any) when going back
    mediaCache.cancelAll();

    setIsContentVisible(false); // Fade out
    // Dispatch map change immediately to start map transition in parallel
    dispatch({ type: "SET_CURRENT_MAP", payload: defaultFolder });
    setTimeout(() => {
      cleanupAllVideos();
      dispatch({ type: "SET_SELECTED_DATA", payload: false });
      dispatch({ type: "SET_EVENT_DATA", payload: null });
      dispatch({
        type: "SET_MEDIA_STATE",
        payload: {
          folder: "",
          hasVideo: false,
          videoType: null,
          hasStatic: false,
          staticType: null,
        },
      });
      
      // Trigger fade-in after a brief delay
      setTimeout(() => {
        setIsContentVisible(true); 
      }, 50);
      
    }, transitionConfig.contentFadeOutMS); // Match CSS transition duration
  }

  // If a media fails to load with HTML content (server returned index.html),
  // attempt a small retry and then force a full reload that re-opens the same entry.
  const handleMediaError = async (mediaUrl) => {
    try {
      // Try a light HEAD request to inspect content-type
      const res = await fetch(mediaUrl, { method: "HEAD", cache: "no-store" });
      const ct = res.headers.get("content-type") || "";
      if (/text\/html/i.test(ct)) {
        // Server returned HTML instead of video — prepare to reload and reopen
        const reopenId = eventData?.id;
        if (reopenId) {
          // Track retries to avoid reload loops
          const key = `reopen-retries-${reopenId}`;
          const retries = parseInt(sessionStorage.getItem(key) || "0", 10);
          if (retries >= 2) {
            console.warn(
              "Media failed after retries, not reloading again:",
              mediaUrl,
            );
            return;
          }
          sessionStorage.setItem(key, String(retries + 1));
          sessionStorage.setItem("reopen-id", String(reopenId));
          // Give the browser a moment to settle then reload
          setTimeout(() => location.reload(), 250);
        } else {
          // no event id — just reload once
          if (!sessionStorage.getItem("reopen-once")) {
            sessionStorage.setItem("reopen-once", "1");
            setTimeout(() => location.reload(), 250);
          }
        }
      } else {
        // Not HTML; let the normal video element handle playback errors
        console.debug(
          "Media HEAD returned non-HTML content-type:",
          ct,
          mediaUrl,
        );
      }
    } catch (err) {
      console.error("Error probing media URL head:", err, mediaUrl);
      // As a fallback, attempt a reload once
      if (!sessionStorage.getItem("reopen-once")) {
        sessionStorage.setItem("reopen-once", "1");
        setTimeout(() => location.reload(), 250);
      }
    }
  };

  // Determine which video folder to play
  // Landscape: Play only if event selected.
  // Portrait: Always play (loop if directory, event if selected).
  let globalVideoFolder = "";
  if (selectedData) {
    globalVideoFolder = mediaState.folder;
  }
  //  else if (isPortrait) {
  //   globalVideoFolder = mediaConfig.defaultLoopFolder;
  // }

  // console.log(`[App] Portrait: ${isPortrait}, Selected: ${selectedData}, Video: ${globalVideoFolder}`);

    // Determine visibility class logic
  // Only hide the video if we are in Landscape mode AND (no event is selected OR content is fading out).
  // In Portrait mode, the video is always visible (either loop or event).
  const hideVideo = (!selectedData || !isContentVisible);

  // Determine the correct transition duration for the current state (in or out)
  const currentVideoTransition = hideVideo
    ? transitionConfig.contentFadeOutMS
    : transitionConfig.contentFadeInMS;

  // Class for portrait transition
  const portraitTransitionClass = !isContentVisible && isPortrait ? layoutStyles["content-transitioning"] : "";

  return (
    <>
      <div
        className={layoutStyles["main-container"]}
        style={{
          "--right-map-width": `${rightMapWidth}vw`,
          "--left-map-width": `${leftMapWidth}vw`,
          "--map-gap": `${mapGap}vw`,
          "--map-right-margin": `${mapRightMargin}vw`,
          "--content-transition-duration": `${currentVideoTransition}ms`,
        }}
      >
        <MapView
          mapFolder={currentMap}
          defaultFolder={defaultFolder}
          booth={eventData?.booth}
        />
        <div className={layoutStyles.top}>
          <img 
            src={`${assetPaths.imagesRootPath}${assetPaths.bgLandscape}`} 
            alt="" 
            className={layoutStyles.bgLandscape}
          />
          <img 
            src={`${assetPaths.imagesRootPath}${assetPaths.bgPortrait}`} 
            alt="" 
            className={layoutStyles.bgPortrait}
          />
        </div>
        
        {/* Global Video Player Wrapper (Provides persistent border/bg) */}
        <div className={`${layoutStyles["video-wrapper"]} ${
            hideVideo ? layoutStyles["hidden-in-landscape"] : ""
          }`}>
          <MediaViewer
            folder={globalVideoFolder}
            className={`${layoutStyles["global-video"]} ${portraitTransitionClass}`}
          />
        </div>
      </div>
      <div className={layoutStyles["top-container"]}>
        <div className={layoutStyles["text-container"]}></div>
      </div>

      <div
        className={`${layoutStyles["bottom-container"]} ${
          isContentVisible ? layoutStyles.contentVisible : ""
        }`}
        style={{
          "--content-width": `${contentWidth}vw`,
        }}
      >
        {!selectedData && <DirectoryView onItemClick={handleClick} />}

        {selectedData && eventData && (
          <DetailView
            handleMediaError={handleMediaError}
            handleBackClick={handleBackClick}
          />
        )}

        {/* blink container removed — positioning circle not used anymore */}
      </div>
    </>
  );
}

export default App;
