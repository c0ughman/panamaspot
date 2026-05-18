import type { NextConfig } from "next";

const nextConfig: NextConfig = {
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
