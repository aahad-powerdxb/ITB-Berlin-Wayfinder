import React from "react";
import { assetPaths } from "../config/config.js";

import { useStateContext } from "../context/StateContext";
import { useMedia } from "../hooks/useMedia";
import styles from "../css/DetailView.module.css";

const DetailView = ({ handleBackClick }) => {
  const { state } = useStateContext();
  const { eventData } = state;
  const { logoSource } = useMedia();

  if (!eventData) return null;

  return (
    <div className={styles["event-container"]}>
      <div className={styles["inner-first"]}>
        <div className={styles.logoContainer}>
          <img
            alt=""
            src={logoSource}
            className={styles["img-first"]}
            onError={(e) => {
              try {
                const cur = e.target.getAttribute("src") || "";
                if (/\.png$/i.test(cur)) {
                  e.target.src = cur.replace(/\.png$/i, ".jpg");
                  return;
                }
              } catch (err) {
                // ignore
              }
              e.target.style.display = "none";
            }}
          />
        </div>

        {/* MediaViewer has been moved to App.jsx for global positioning */}
        {/* We keep this empty container if needed for layout spacing, 
            or rely on the global element positioning over it */}
        {/* <div className={styles.bgImage}></div> */}
      </div>

      <div className={styles["inner-second"]}>
        <h1 dangerouslySetInnerHTML={{ __html: eventData.title }}></h1>
        <div className={styles["scroll-container"]}>
          <p dangerouslySetInnerHTML={{ __html: eventData.content }}></p>
        </div>
      </div>

      <div className={styles["inner-third"]}>
        <button onClick={handleBackClick}>
          <img src={`${assetPaths.imagesRootPath}back.png`} alt="Back" />
        </button>
      </div>
    </div>
  );
};

export default DetailView;
