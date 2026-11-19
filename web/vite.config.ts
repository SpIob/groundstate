import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Static build only. Hash routes live in src/router.ts; no server, no rewrites.
export default defineConfig({
  plugins: [react()],
});
