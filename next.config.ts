import type { NextConfig } from "next";

/* Static export: `next build` writes plain HTML/CSS/JS to `out/`.
   The post-build script (scripts/build-static.mjs) then strips the
   Next.js runtime so the output is pure static HTML.

   trailingSlash is left at the default (false) so each page is a single
   <name>.html file served at /<name>, instead of a /<name>/index.html
   folder. Single canonical per URL, no /index.html clutter. */
const nextConfig: NextConfig = {
  output: "export",
  images: { unoptimized: true },
};

export default nextConfig;
