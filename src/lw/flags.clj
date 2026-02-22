(ns lw.flags
  "Capa principal de configuraciones custom (layer lw)
   Aquí gestionamos los feature flags para modificar el comportamiento base (upstream)."
  (:require [clojure.string :as str]))

(defn is-enabled?
  "Lee una variable de entorno con el prefijo LW_FEATURE_X y devuelve true si es 'true'"
  [flag-name]
  (let [env-val (System/getenv (str "LW_FEATURE_" (str/upper-case (name flag-name))))]
    (= (str/lower-case (or env-val "false")) "true")))
