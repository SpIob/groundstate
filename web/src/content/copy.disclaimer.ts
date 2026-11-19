// Copy slot `disclaimer` (docs/web/PAGES.md P4). PLACEHOLDER - real copy is
// drafted and approved by Mico in task W-004 and placed by /gs-web-copy
// (task W-007). The version line renders from `version`; the
// disclaimer_version on candidate JSON must match it.

export interface CopyDisclaimer {
  paragraphs: string[];
  version: number;
}

export const copyDisclaimer: CopyDisclaimer = {
  paragraphs: [
    "Disclaimer copy pending approval (task W-004).",
  ],
  version: 1,
};
