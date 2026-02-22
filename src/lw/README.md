# Estructura del repositorio

Este fork de Metabase utiliza la siguiente topología de ramas y directorios:

### Ramas de Git

- `main`: Actúa como **espejo (mirror)** del repositorio oficial (`upstream`). Nunca debes trabajar directamente en esta rama, solo se utiliza para traer los últimos cambios oficiales.
- `custom`: Es la rama **principal de desarrollo**. Todos los features, resoluciones de integraciones, UI modificado, y correcciones van en esta o en ramas desprendidas de `custom`.

### El directorio `lw/`

Para evitar conflictos (merge conflicts) masivos al actualizar con `main`, las modificaciones y el código nuevo de negocio reside preferentemente en la capa aislada:

- Backend: `src/lw/*`
- Frontend: `frontend/src/lw/*`

#### Feature Flags

Las características personalizadas o modificaciones se activan usando variables de entorno con el prefijo `LW_FEATURE_`.
Ejemplo: `LW_FEATURE_LOGIN_CUSTOM=true`.
Las utilidades que leen esto residen en:

- Backend: `src/lw/flags.clj` (`(lw.flags/is-enabled? :login-custom)`)
- Frontend: `frontend/src/lw/flags.ts` (`isFeatureEnabled('LOGIN_CUSTOM')`)
