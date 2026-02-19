import React, { useEffect, useRef } from "react";
import Column from "../components/Column";
import ListItem from "../components/ListItem";
import { useStateContext } from "../context/StateContext";
import styles from "../css/DirectoryView.module.css";
import { mediaCache } from "../utils/MediaCache";
import { mediaConfig, directoryConfig } from "../config/config.js";
import { useMediaQuery } from "../hooks/useMediaQuery";

const DirectoryView = ({ onItemClick }) => {
  const { state } = useStateContext();
  const { groupedData, columnRanges, boothSortedData } = state;
  const observerRef = useRef(null);
  const isPortrait = useMediaQuery("(orientation: portrait)");

  useEffect(() => {
    // Disable preloading in portrait mode to prioritize the global footer video
    if (!groupedData || isPortrait) {
      if (!groupedData) console.log("[DirectoryView] No groupedData yet.");
      if (isPortrait) console.log("[DirectoryView] Preloading disabled in Portrait mode.");
      return;
    }

    console.log("[DirectoryView] Starting IntersectionObserver setup.");

    // Track visible items
    const visibleItems = new Set();
    let intervalId = null;

    // Disconnect old observer if any
    if (observerRef.current) observerRef.current.disconnect();

    observerRef.current = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          const id = entry.target.dataset.id;
          if (!id) return;
          
          if (entry.isIntersecting) {
            visibleItems.add(id);
          } else {
            visibleItems.delete(id);
          }
        });
      },
      { rootMargin: "0px" } 
    );

    // Start interval to process visible items slowly
    // This prevents flooding the queue and allows aborts to settle
    intervalId = setInterval(() => {
        if (visibleItems.size === 0) return;

        // Take one item from the set (iterators return in insertion order)
        const id = visibleItems.values().next().value;
        if (id) {
            // Remove it from the set so we don't process it again immediately
            visibleItems.delete(id);
            
            console.log(`[DirectoryView] Preloading item: ${id}`);
            const folder = `${mediaConfig.mediaRootPath}${id}`;
            // Prioritize logos first
            mediaCache.preloadContent(`${folder}/logo.png`);
            // Then opportunistically load video
            mediaCache.preloadContent(`${folder}/video.mp4`);
        }
    }, 200); // Process 1 item every 200ms

    // Observe all list items using a more direct selector
    // We target the elements with data-id directly inside our container
    const container = document.querySelector(`.${styles["data-container"]}`);
    let elements = [];
    if (container) {
        elements = container.querySelectorAll('[data-id]');
    } else {
        // Fallback: try to find data-id anywhere on the page if container not found
        elements = document.querySelectorAll('[data-id]');
    }
    
    console.log(`[DirectoryView] Found ${elements.length} elements to observe.`);
    elements.forEach((el) => observerRef.current.observe(el));

    return () => {
      if (observerRef.current) observerRef.current.disconnect();
      if (intervalId) clearInterval(intervalId);
    };
  }, [groupedData, boothSortedData, isPortrait]);

  return (
    <div>
      <div className={styles["data-container"]}>
        {isPortrait ? (
          /* Portrait Layout: 2 Columns Split by Booth Number logic */
          /* Col 1: Integers 1-30 */
          /* Col 2: Integers 31+ AND any alphanumeric (e.g. "17 & B") */
          <div className={styles.portraitGrid}>
             <div className={styles.portraitCol1}>
                {boothSortedData
                  .filter(d => {
                    const b = String(d.booth);
                    // Check if strictly integer and <= split point
                    return /^\d+$/.test(b) && parseInt(b, 10) <= directoryConfig.portraitSplitBooth;
                  })
                  .map(data => (
                    <ListItem key={data.id} data={data} onClick={onItemClick} />
                  ))
                }
             </div>
             <div className={styles.portraitCol2}>
                {boothSortedData
                  .filter(d => {
                    const b = String(d.booth);
                    // Check if NOT (strictly integer <= split point)
                    return !(/^\d+$/.test(b) && parseInt(b, 10) <= directoryConfig.portraitSplitBooth);
                  })
                  .map(data => (
                    <ListItem key={data.id} data={data} onClick={onItemClick} />
                  ))
                }
             </div>
          </div>
        ) : (
          /* Landscape Layout: 3 Columns by Alphabet */
          <>
            <Column
              groupedData={groupedData}
              startLetter={columnRanges[0].start}
              endLetter={columnRanges[0].end}
              className={styles.first}
              onItemClick={onItemClick}
            />
            <Column
              groupedData={groupedData}
              startLetter={columnRanges[1].start}
              endLetter={columnRanges[1].end}
              className={styles.second}
              onItemClick={onItemClick}
            />
            <Column
              groupedData={groupedData}
              startLetter={columnRanges[2].start}
              endLetter={columnRanges[2].end}
              className={styles.third}
              onItemClick={onItemClick}
            />
          </>
        )}
      </div>
    </div>
  );
};

export default DirectoryView;
