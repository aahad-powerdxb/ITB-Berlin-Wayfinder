import React, { useMemo } from "react";
import ListItem from "./ListItem";
import styles from "../css/DirectoryView.module.css";

function Column({ groupedData, startLetter, endLetter, className, onItemClick }) {
  const columnItems = useMemo(() => {
    const items = [];
    // Get all available starting letters from the data and sort them
    const letters = Object.keys(groupedData).sort();
    
    // Check each available letter against our alphabetical range
    letters.forEach(letter => {
      // As long as the letter falls alphabetically between startLetter and endLetter
      if (letter >= startLetter && letter <= endLetter) {
        items.push(
          // Add letter heading
          <div key={`heading-${letter}`} className={styles["line-text"]}>
            {letter}
          </div>,
          // Add all items for this letter
          ...groupedData[letter].map(data => (
            <ListItem
              key={data.id}
              data={data}
              onClick={onItemClick}
            />
          ))
        );
      }
    });
    
    return items;
  }, [groupedData, startLetter, endLetter, onItemClick]);

  return (
    <div className={className}>
      {columnItems}
    </div>
  );
}

export default Column;