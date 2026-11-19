// Copy slot `about` (docs/web/PAGES.md P2). PLACEHOLDER - real copy is
// drafted and approved by Mico in task W-004 and placed by /gs-web-copy
// (task W-007). The build must not ship these strings to production pages;
// the About page renders them only as a development stub.

export interface CopyAbout {
  paragraphs: string[];
}

export const copyAbout: CopyAbout = {
  paragraphs: [
    "About copy pending approval (task W-004).",
  ],
};
