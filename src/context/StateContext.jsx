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

  // 1. Intercept data and safely uppercase titles while ignoring HTML tags
  const processedDatas = useMemo(() => {
    return basicDatas.map((item) => {
      if (typeof item.title === "string") {
        const upperTitle = item.title.replace(/(^|>)([^<]+)(<|$)/g, (match, p1, p2, p3) => {
          return p1 + p2.toUpperCase() + p3;
        });
        return { ...item, title: upperTitle };
      }
      return item;
    });
  }, []);

  // 2. Use processedDatas instead of basicDatas
  const groupedData = useMemo(() => {
    return groupItemsAlphabetically(processedDatas);
  }, [processedDatas]);

  // 3. Use processedDatas instead of basicDatas for booth sorting
  const boothSortedData = useMemo(() => {
    const processed = [];
    
    processedDatas.forEach(item => {
      const boothStr = String(item.booth);
      if (boothStr.includes(" & ")) {
        const parts = boothStr.split(" & ");
        parts.forEach((part, index) => {
          processed.push({
            ...item,
            id: `${item.id}_split_${index}`,
            booth: part.trim(),
          });
        });
      } else {
        processed.push(item);
      }
    });

    return processed.sort((a, b) => {
      const boothA = String(a.booth).toUpperCase();
      const boothB = String(b.booth).toUpperCase();
      return boothA.localeCompare(boothB, undefined, { numeric: true, sensitivity: 'base' });
    });
  }, [processedDatas]);

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