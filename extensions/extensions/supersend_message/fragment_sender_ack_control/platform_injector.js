// platform_injector.js
// Importa y usa el módulo de inyección

import { PlatformInjector } from './injector_multiplatform.js';

export const injector = new PlatformInjector();

// Función simplificada para enviar
export async function sendToPlatform(platform, message) {
  return injector.dispatch(platform, message);
}
