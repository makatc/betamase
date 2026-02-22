/**
 * Custom lw layer configuration
 * This file manages feature flags reading environment variables prefixed with LW_FEATURE_X
 * Example: LW_FEATURE_CUSTOM_LOGIN=true
 */

export const isFeatureEnabled = (flagName: string): boolean => {
  // En frontend las variables de entorno deben estar expuestas por Rspack/Webpack o injectadas globalmente
  // Dependiendo de la integración, esto podría chequear process.env.LW_FEATURE_X o window.LW_CONFIG

  const envName = `LW_FEATURE_${flagName.toUpperCase()}`;

  // Asumiendo que las proveemos via process.env en el build
  return process.env[envName] === "true";
};
