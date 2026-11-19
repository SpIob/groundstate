import { useEffect, useState } from "react";
import { onRouteChange, type Route } from "./router";
import { Landing } from "./pages/Landing";
import { About } from "./pages/About";
import { Contacts } from "./pages/Contacts";
import { Disclaimer } from "./pages/Disclaimer";
import { Explore } from "./pages/Explore";
import { DOMAINS } from "./content/domains";

export default function App() {
  const [route, setRoute] = useState<Route>({ page: "landing" });

  useEffect(() => onRouteChange(setRoute), []);

  switch (route.page) {
    case "landing":
      return <Landing />;
    case "sub":
      if (route.sub === "about") return <About />;
      if (route.sub === "contacts") return <Contacts />;
      return <Disclaimer />;
    case "explore": {
      // PAGES.md Routes: "Unknown route: show Landing and nothing else". The
      // defined explore routes carry registry ids, so a domain or child
      // segment outside the registry is an unknown route, not an empty
      // Explore view.
      const domain = route.domain ? DOMAINS.find((d) => d.id === route.domain) : undefined;
      if (route.domain && !domain) return <Landing />;
      if (route.child && !domain?.children.some((c) => c.id === route.child)) return <Landing />;
      return <Explore domain={route.domain} child={route.child} />;
    }
  }
}
