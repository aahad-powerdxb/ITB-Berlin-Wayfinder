import React from "react";
import styles from "../css/DirectoryView.module.css";

function ListItem({ data, onClick }) {
  return (
    <div
      key={data.id}
      data-id={data.id} // Add data-id for intersection observer
      onClick={() => onClick(data)}
      className={styles.link}
    >
      <span dangerouslySetInnerHTML={{ __html: data.title }}></span>
      <span>{data.booth}</span>
    </div>
  );
}

export default ListItem;