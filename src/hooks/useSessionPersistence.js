import { useEffect } from "react";
import { useStateContext } from "../context/StateContext";
import basicDatas from "../data/basicDatas.json";

export const useSessionPersistence = () => {
  const { dispatch } = useStateContext();

  useEffect(() => {
    try {
      const reopenId = sessionStorage.getItem("reopen-id");
      if (reopenId) {
        const idNum = parseInt(reopenId, 10);
        const found = basicDatas.find((d) => Number(d.id) === idNum);
        if (found) {
          sessionStorage.removeItem("reopen-id");
          dispatch({ type: "SET_EVENT_DATA", payload: found });
          dispatch({ type: "SET_SELECTED_DATA", payload: true });
          dispatch({
            type: "SET_MEDIA_STATE",
            payload: {
              folder: `/media/${found.id}`,
              hasVideo: false,
              videoType: null,
              hasStatic: false,
              staticType: null,
            },
          });
        } else {
          sessionStorage.removeItem("reopen-id");
        }
      }
    } catch (e) {
      // ignore
    }
  }, [dispatch]);
};
