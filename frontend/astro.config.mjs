import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://pongelupe.github.io',
  base: process.env.NODE_ENV === 'production' ? '/na_boca_do_sol_podcast' : undefined,
  output: 'static',
  integrations: [sitemap()],
});
