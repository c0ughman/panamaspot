import type { NextConfig } from "next";

/* Static export: `next build` writes plain HTML/CSS/JS to `out/`.
   The post-build script (scripts/build-static.mjs) then strips the
   Next.js runtime so the output is pure static HTML. */
const nextConfig: NextConfig = {
  output: "export",
  trailingSlash: true,
  images: { unoptimized: true },
};

export default nextConfig;
