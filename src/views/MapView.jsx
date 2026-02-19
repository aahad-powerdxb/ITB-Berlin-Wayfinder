import React, { useEffect, useState } from "react";
import styles from "../css/MapView.module.css";
import { transitionConfig } from "../config/config.js";

// Generic image component to reduce duplication
const CrossFadeImage = ({ srcA, srcB, visibleSlot, transitioning, className, onError }) => (
  <div className={className}>
    {srcA && (
      <img
        src={srcA}
        alt=""
        className={`
          ${styles.mapImage}
          ${visibleSlot === "slotA" ? styles.visible : ""}
          ${transitioning && visibleSlot !== "slotA" ? styles.withTransition : ""}
        `}
        onError={onError}
      />
    )}
    {srcB && (
      <img
        src={srcB}
        alt=""
        className={`
          ${styles.mapImage}
          ${visibleSlot === "slotB" ? styles.visible : ""}
          ${transitioning && visibleSlot !== "slotB" ? styles.withTransition : ""}
        `}
        onError={onError}
      />
    )}
  </div>
);

const MapView = ({ mapFolder, defaultFolder, booth }) => {
  // State holds the paths for TWO separate map views (Left/Narrow and Right/Wide)
  // Each view has two slots (A/B) for cross-fading
  // const [leftMaps, setLeftMaps] = useState({ slotA: `${defaultFolder}/2.png`, slotB: null });
  const [rightMaps, setRightMaps] = useState({ slotA: `${defaultFolder}/1.png`, slotB: null });
  
  const [activeSlot, setActiveSlot] = useState("slotA"); // "slotA" or "slotB" is visible
  const [isTransitioning, setIsTransitioning] = useState(false);

  // Calculate the total duration for the map's fade effect
  const mapFadeDuration =
    transitionConfig.contentFadeInMS + transitionConfig.contentFadeOutMS;

  useEffect(() => {
    // Determine the target folder (current or default)
    const targetFolder = mapFolder || defaultFolder;
    
    // Construct new URLs
    // const newLeftMap = `${targetFolder}/2.png`;
    const newRightMap = `${targetFolder}/1.png`;

    // Check against currently visible maps to see if update is needed
    // const currentLeft = activeSlot === "slotA" ? leftMaps.slotA : leftMaps.slotB;
    
    // Simple check: if the main map URL hasn't changed, do nothing
    // (Assuming both maps change together)
    // if (newLeftMap === currentLeft) return;

    // Start Transition
    const nextSlot = activeSlot === "slotA" ? "slotB" : "slotA";
    
    // Load new maps into the hidden slot
    // setLeftMaps(prev => ({ ...prev, [nextSlot]: newLeftMap }));
    setRightMaps(prev => ({ ...prev, [nextSlot]: newRightMap }));
    
    // Trigger the fade
    setIsTransitioning(true);
    setActiveSlot(nextSlot);

    // Cleanup transition state after animation
    const timer = setTimeout(() => {
      setIsTransitioning(false);
    }, mapFadeDuration);

    return () => clearTimeout(timer);
  }, [mapFolder, defaultFolder]);

  return (
    <div
      className={styles["map-container"]}
      style={{ "--map-fade-duration": `${mapFadeDuration}ms` }}
    >
      {/* Left Map (Narrower, 2.png) */}
    <div className={styles["left-map-wrapper"]}>
      <img
        src={`${defaultFolder}/2.png`}
        alt=""
        className={`${styles.mapImage} ${styles.visible}`}
        onError={(e) => {
          console.warn(`Left map not found: ${e.target.src}`);
          e.target.style.opacity = 0; 
        }}
      />
    </div>

      {/* Right Map (Wider, 1.png) */}
      <CrossFadeImage 
        srcA={rightMaps.slotA} 
        srcB={rightMaps.slotB} 
        visibleSlot={activeSlot} 
        transitioning={isTransitioning}
        className={styles["right-map-wrapper"]}
        onError={(e) => {
           console.warn(`Right map not found: ${e.target.src}`);
           e.target.style.opacity = 0;
        }}
      />
    </div>
  );
};

export default MapView;
