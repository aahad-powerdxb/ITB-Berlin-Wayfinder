import React from 'react';
import { FixedSizeList as List } from 'react-window';
import AutoSizer from 'react-virtualized-auto-sizer';

// VirtualizedColumn: generic virtualized list wrapper
// Props:
// - items: array of items to render
// - itemHeight: number (px)
// - className: optional
// - onItemClick: function(item)
// - renderItem: optional render function (item) => node; otherwise default rendering
export default function VirtualizedColumn({ items = [], itemHeight = 80, className = '', onItemClick = () => {}, renderItem }) {
  if (!items || items.length === 0) return <div className={`column ${className}`} />;

  const Row = ({ index, style, data }) => {
    const item = data.items[index];
    const handleClick = () => {
      if (!item.inactive) onItemClick(item);
    };

    return (
      <div style={style} className={`virtual-item ${item.inactive ? 'inactive' : ''}`} onClick={handleClick}>
        {renderItem ? (
          renderItem(item)
        ) : (
          <div className="item-inner">
            <div className="item-title" dangerouslySetInnerHTML={{ __html: item.title }} />
            <div className="item-content" dangerouslySetInnerHTML={{ __html: item.content }} />
          </div>
        )}
      </div>
    );
  };

  return (
    <div className={`column ${className}`}>
      <AutoSizer>
        {({ height, width }) => (
          <List
            height={height}
            itemCount={items.length}
            itemSize={itemHeight}
            width={width}
            itemData={{ items }}
          >
            {Row}
          </List>
        )}
      </AutoSizer>
    </div>
  );
}
