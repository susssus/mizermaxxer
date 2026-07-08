import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";
import vercel from "@astrojs/vercel";

const site = process.env.SITE_URL ?? "https://mizermaxxer.org";

export default defineConfig({
  site,
  output: "static",
  adapter: vercel(),
  integrations: [sitemap()],
});
