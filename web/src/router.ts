// Hash router, hand-written, no library (docs/web/SCAFFOLD.md).
// Routes from docs/web/PAGES.md: #/ #/about #/contacts #/disclaimer
// #/explore #/explore/<domain> #/explore/<domain>/<child>.
// Unknown route: show Landing and nothing else (no 404 page).

export type SubPage = "about" | "contacts" | "disclaimer";

export type Route =
  | { page: "landing" }
  | { page: "sub"; sub: SubPage }
  | { page: "explore"; domain?: string; child?: string };

export function parseHash(hash: string): Route {
  const clean = hash.replace(/^#\/?/, "");
  const parts = clean.split("/").filter(Boolean);
  if (parts.length === 0) {
    return { page: "landing" };
  }
  if (parts[0] === "about" || parts[0] === "contacts" || parts[0] === "disclaimer") {
    return { page: "sub", sub: parts[0] };
  }
  if (parts[0] === "explore") {
    return { page: "explore", domain: parts[1], child: parts[2] };
  }
  return { page: "landing" };
}

export function hrefFor(route: Route): string {
  switch (route.page) {
    case "landing":
      return "#/";
    case "sub":
      return `#/${route.sub}`;
    case "explore": {
      let path = "#/explore";
      if (route.domain) path += `/${route.domain}`;
      if (route.domain && route.child) path += `/${route.child}`;
      return path;
    }
  }
}

export function onRouteChange(cb: (route: Route) => void): () => void {
  const handler = () => cb(parseHash(window.location.hash));
  window.addEventListener("hashchange", handler);
  handler();
  return () => window.removeEventListener("hashchange", handler);
}
