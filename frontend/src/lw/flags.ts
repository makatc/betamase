/**
 * Custom lw layer configuration
 * Feature flags leídos de process.env (embebidos por rspack en build time).
 *
 * Para activar: pasar las vars al proceso de build:
 *   LW_FEATURE_AI_CHAT_WIDGET=true bun run build-hot
 *
 * Para cambiar la URL del middleware AI:
 *   REACT_APP_AI_URL=http://mi-servidor:8001 bun run build-hot
 */

export const isFeatureEnabled = (flagName: string): boolean => {
  const envName = `LW_FEATURE_${flagName.toUpperCase()}`;
  return process.env[envName] === "true";
};

/**
 * Get the AI Middleware base URL
 * Default: http://localhost:8001
 * Override: REACT_APP_AI_URL env var al momento del build
 */
export const getAIMiddlewareURL = (): string => {
  return process.env.REACT_APP_AI_URL || "http://localhost:8001";
};
