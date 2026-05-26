import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Ready for next/image with the Pexels CDN (used by the home + templates).
  images: {
    remotePatterns: [{ protocol: "https", hostname: "images.pexels.com" }],
  },
  async rewrites() {
    return [
      {
        source: "/funnels/:slug",
        destination: "/funnels/:slug.html",
      },
    ];
  },
};

export default nextConfig;
