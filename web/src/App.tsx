import { useEffect, useState } from "react";
import { onRouteChange, type Route } from "./router";
import { Landing } from "./pages/Landing";
import { About } from "./pages/About";
import { Contacts } from "./pages/Contacts";
import { Disclaimer } from "./pages/Disclaimer";
import { Explore } from "./pages/Explore";

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
    case "explore":
      return <Explore domain={route.domain} child={route.child} />;
  }
}
