import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: 'drive.google.com', // Whitelist Google Drive's host
        port: '',
        pathname: '/uc/**', // Allow all paths under the /uc (user content) endpoint
      },
    ],
  },
};

export default nextConfig;