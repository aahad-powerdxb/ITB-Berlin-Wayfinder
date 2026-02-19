import React, { useMemo } from "react";
import ListItem from "./ListItem";
import styles from "../css/DirectoryView.module.css";

function Column({ groupedData, startLetter, endLetter, className, onItemClick }) {
  // Get all items for this column's letter range
  const columnItems = useMemo(() => {
    const items = [];
    const letters = Object.keys(groupedData).sort();
    
    // Find start and end indices in the letters array
    const startIndex = letters.indexOf(startLetter);
    const endIndex = letters.indexOf(endLetter);
    
    // If valid range, collect all items
    if (startIndex !== -1 && endIndex !== -1) {
      for (let i = startIndex; i <= endIndex; i++) {
        const letter = letters[i];
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
    }
    
    return items;
  }, [groupedData, startLetter, endLetter, onItemClick]);

  return (
    <div className={className}>
      {columnItems}
    </div>
  );
}

export default Column;