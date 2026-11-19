// Contact tiles (docs/web/PAGES.md P3). URLs and the mailto address come from
// Mico (task W-004). Never invent a handle or address: every value below is
// null until Mico supplies it. A tile with no URL renders unlinked and prints
// UNSET; deploy is blocked while any tile is UNSET unless Mico removes it.

export interface ContactTile {
  id: string;
  label: string;
  url: string | null;
}

export const CONTACTS: ContactTile[] = [
  { id: "x", label: "X", url: null },
  { id: "instagram", label: "Instagram", url: null },
  { id: "youtube", label: "YouTube", url: null },
  { id: "tiktok", label: "TikTok", url: null },
  { id: "github", label: "GitHub", url: null },
  { id: "email", label: "Email", url: null },
];
