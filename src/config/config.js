export const mapConfig = {
  mapsRootPath: "/assets/images/maps/",
  defaultFolder: "default", // Name of the default folder
};

export const transitionConfig = {
  // Duration for the main content to fade OUT
  contentFadeOutMS: 400,
  // Duration for the main content to fade IN
  contentFadeInMS: 400,
};

export const mediaConfig = {
  mediaRootPath: "/assets/media/",
  // Folder containing the default loop video (video.mp4) and poster (video.jpg)
  defaultLoopFolder: "/assets/media/default_loop",
};

// New config for general assets
export const assetPaths = {
  imagesRootPath: "/assets/images/",
  bgLandscape: "bgImage_landscape.png",
  bgPortrait: "bgImage_portrait.png",
};

// Configuration for layout dimensions (in VW units)
export const layoutConfig = {
  // Width of the main (right) map in VW
  rightMapWidthVW: 33,
  // Width of the secondary (left) map in VW
  leftMapWidthVW: 8,
  // Gap between maps in VW
  mapGapVW: 0,
  // Right margin of the entire map container in VW
  mapRightMarginVW: 0,
  // Space reserved between the content area and the maps in VW
  contentRightMarginVW: -1,
};

// Configuration for Directory View columns
export const directoryConfig = {
  // Landscape: Define the 3 columns by alphabet ranges
  landscapeColumnRanges: [
    { start: "A", end: "E" },
    { start: "H", end: "R" },
    { start: "S", end: "Z" },
  ],
  // Portrait: The integer booth number to split the list at.
  // Column 1: <= splitBooth
  // Column 2: > splitBooth
  portraitSplitBooth: 18,
};
