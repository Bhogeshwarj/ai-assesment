import type { NextConfig } from "next";

// "standalone" output is only for the Docker build (frontend/Dockerfile copies
// .next/standalone into the runner image). On Vercel this must NOT be set -
// Vercel's own build pipeline expects the default output format, and
// "standalone" breaks it, producing a 404: NOT_FOUND on every route.
const nextConfig: NextConfig = {
  ...(process.env.BUILD_STANDALONE === "true" ? { output: "standalone" as const } : {}),
};

export default nextConfig;
