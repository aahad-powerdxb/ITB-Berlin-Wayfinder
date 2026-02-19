import { useMemo } from "react";
import { useStateContext } from "../context/StateContext";

/**
 * A simple hook to derive media-related sources from the global state.
 * It reads the correct folder path from `mediaState` which is set in App.jsx
 * and uses it to construct the full path for the logo image.
 * This hook is now purely for deriving data and has no side effects.
 */
export const useMedia = () => {
  const { state } = useStateContext();
  // We trust that `mediaState.folder` has been set correctly in `App.jsx`
  // with the full, correct path from the config (e.g., /assets/media/123).
  const { folder } = state.mediaState;

  // Construct the full path to the logo using the reliable folder path from state.
  const logoSource = useMemo(() => {
    if (!folder) {
      return null;
    }
    // Append the standard logo filename to the folder path.
    return `${folder}/logo.png`;
  }, [folder]);

  return { logoSource };
};


