import type { NextConfig } from "next";

const isGithubPages = process.env.GITHUB_ACTIONS === "true";
const repoName = "sport";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  turbopack: {},
  poweredByHeader: false,
  output: "export",
  trailingSlash: true,
  images: { unoptimized: true },
  basePath: isGithubPages ? `/${repoName}` : "",
  assetPrefix: isGithubPages ? `/${repoName}/` : undefined,
  experimental: {
    optimizePackageImports: ["lucide-react"],
  },
};

export default nextConfig;
