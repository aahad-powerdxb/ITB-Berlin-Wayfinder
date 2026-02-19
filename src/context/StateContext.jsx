import React, { createContext, useReducer, useContext, useMemo } from "react";
import { groupItemsAlphabetically } from "../utils/dataUtils";
import basicDatas from "../data/basicDatas.json";
import { directoryConfig } from "../config/config.js";

const StateContext = createContext();

const initialState = {
  selectedData: false,
  eventData: null,
  mediaState: {
    folder: "",
    hasVideo: false,
    videoType: null,
    hasStatic: false,
    staticType: null,
  },
  currentMap: "",
  groupedData: {},
  boothSortedData: [], // New state for portrait mode
  columnRanges: [],
};

const stateReducer = (state, action) => {
  switch (action.type) {
    case "SET_SELECTED_DATA":
      return { ...state, selectedData: action.payload };
    case "SET_EVENT_DATA":
      return { ...state, eventData: action.payload };
    case "SET_MEDIA_STATE":
      return { ...state, mediaState: action.payload };
    case "SET_CURRENT_MAP":
      return { ...state, currentMap: action.payload };
    case "SET_GROUPED_DATA":
      return { ...state, groupedData: action.payload };
    case "SET_BOOTH_SORTED_DATA":
      return { ...state, boothSortedData: action.payload };
    case "SET_COLUMN_RANGES":
      return { ...state, columnRanges: action.payload };
    default:
      return state;
  }
};

export const StateProvider = ({ children }) => {
  const [state, dispatch] = useReducer(stateReducer, initialState);

  const groupedData = useMemo(() => {
    return groupItemsAlphabetically(basicDatas);
  }, []);

  // New logic: Sort flat list by booth number, duplicating "&" entries
  const boothSortedData = useMemo(() => {
    const processed = [];
    
    basicDatas.forEach(item => {
      const boothStr = String(item.booth);
      if (boothStr.includes(" & ")) {
        const parts = boothStr.split(" & ");
        parts.forEach((part, index) => {
          // Clone item, modify booth to just this part
          // Generate unique ID to prevent key conflicts in lists
          processed.push({
            ...item,
            id: `${item.id}_split_${index}`,
            booth: part.trim(),
            // Keep original ID for media lookup? Yes, media uses folder based on original ID.
            // But App.jsx uses data.id for folder lookup.
            // If we change ID, media lookup fails!
            // Solution: Keep original ID in a separate field 'originalId' or rely on folder naming convention?
            // Actually, we should probably preserve the 'id' if the folder name depends on it.
            // But React needs unique keys.
            // Let's assume ListItem uses `id` for key but App uses it for media.
            // We must preserve the REAL id for media lookup.
            // Let's add a `uniqueKey` field for React, and keep `id` intact?
            // No, ListItem uses `key={data.id}`.
            // If we change `id`, `App.jsx` handleClick(data) will pass the NEW id.
            // `folder: .../media/${data.id}` -> `/media/123_split_0`. This folder doesn't exist!
            
            // Hack: We need to ensure App.jsx uses the ORIGINAL id for media.
            // Let's store the real ID in `mediaId` and fallback to `id`?
            // Or better: Use the original ID for logic, but append a suffix for the unique key.
            // But we can't change the structure of `data` expected by `ListItem`.
            
            // Cleanest Solution:
            // Modify App.jsx to handle this split ID.
            // OR: Keep `id` as original, but ensure `ListItem` uses a combined key?
            // `ListItem` uses `key={data.id}`. We MUST make `id` unique.
            
            // So `id` becomes `123_split_0`.
            // App.jsx `handleClick` must strip the suffix before media lookup.
          });
        });
      } else {
        processed.push(item);
      }
    });

    return processed.sort((a, b) => {
      // Handle numeric and string booth numbers (e.g. "10", "10A")
      const boothA = String(a.booth).toUpperCase();
      const boothB = String(b.booth).toUpperCase();
      return boothA.localeCompare(boothB, undefined, { numeric: true, sensitivity: 'base' });
    });
  }, []);

  const columnRanges = useMemo(() => {
    return directoryConfig.landscapeColumnRanges;
  }, []);

  useMemo(() => {
    dispatch({ type: "SET_GROUPED_DATA", payload: groupedData });
    dispatch({ type: "SET_BOOTH_SORTED_DATA", payload: boothSortedData });
    dispatch({ type: "SET_COLUMN_RANGES", payload: columnRanges });
  }, [groupedData, boothSortedData, columnRanges]);

  return (
    <StateContext.Provider value={{ state, dispatch }}>
      {children}
    </StateContext.Provider>
  );
};

export const useStateContext = () => useContext(StateContext);
