import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";

const site = process.env.SITE_URL ?? "https://mizermaxxer.org";

export default defineConfig({
  site,
  output: "static",
  integrations: [sitemap()],
});
