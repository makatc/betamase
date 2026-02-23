/**
 * Custom lw layer configuration
 * This file manages feature flags and AI middleware URL
 * Feature flags: LW_FEATURE_X environment variables
 * AI URL: REACT_APP_AI_URL (defaults to localhost:8001 for development)
 */

export const isFeatureEnabled = (flagName: string): boolean => {
  const envName = `LW_FEATURE_${flagName.toUpperCase()}`;
  return process.env[envName] === "true";
};

/**
 * Get the AI Middleware base URL
 * In development: http://localhost:8001 (default)
 * In production: Configure via REACT_APP_AI_URL env var
 */
export const getAIMiddlewareURL = (): string => {
  return process.env.REACT_APP_AI_URL || "http://localhost:8001";
};
