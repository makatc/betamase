(ns metabase.api.ai
  "Custom API endpoints for LW AI integration."
  (:require
   [metabase.api.macros :as api.macros]
   [metabase.driver :as driver]
   [metabase.llm.anthropic :as llm.anthropic]
   [metabase.util.i18n :refer [tru]]
   [metabase.util.log :as log]
   [toucan2.core :as t2]))

(set! *warn-on-reflection* true)

(api.macros/defendpoint :post "/chat"
  "Custom chat assistant endpoint for lw layer."
  :- [:map [:reply :string]]
  [body]
  (let [{:keys [message]} body]
    (log/info "AI Chat request:" message)
    (try
      (let [{:keys [result]} (llm.anthropic/chat-completion
                              {:system "You are a helpful data assistant for Metabase."
                               :messages [{:role "user" :content message}]})]
        {:reply (or (:explanation result) (:sql result) "No pude procesar la respuesta.")})
      (catch Exception e
        (log/error e "Error in AI Chat")
        {:reply (str "Error: " (.getMessage e))}))))

(api.macros/defendpoint :post "/generate-sql"
  "Custom SQL generation endpoint for lw layer."
  :- [:map [:sql :string]]
  [body]
  (let [{:keys [natural_language]} body]
    (log/info "AI SQL generation request:" natural_language)
    (let [database-id (or (:database_id body)
                          (t2/select-one-fn :id :model/Database {:order-by [[:id :asc]]}))]
      (if-not database-id
        (throw (ex-info (tru "No database found for SQL generation.") {:status-code 400}))
        (try
          (let [{:keys [result]} (llm.anthropic/chat-completion
                                  {:system (str "Generate SQL for " (driver/display-name (t2/select-one-fn :engine :model/Database :id database-id))
                                                ". Output JSON with 'sql' and 'explanation'.")
                                   :messages [{:role "user" :content natural_language}]})]
            {:sql (or (:sql result) "")})
          (catch Exception e
            (log/error e "Error in AI SQL Generation")
            {:sql (str "-- Error: " (.getMessage e))})))))

(api.macros/defendpoint :post "/insights"
  "Custom insights endpoint for lw layer."
  :- [:map [:text :string]]
  [body]
  (let [{:keys [dashboard_id data_json]} body]
    (log/info "AI Insights request for dashboard:" dashboard_id)
    (try
      (let [{:keys [result]} (llm.anthropic/chat-completion
                              {:system "Provide a brief insight (1-2 sentences) about the provided chart data."
                               :messages [{:role "user" :content (str "Data: " data_json)}]})]
        {:text (or (:explanation result) (:sql result) "Interesante tendencia en los datos.")})
      (catch Exception e
        (log/error e "Error in AI Insights")
        {:text "Análisis no disponible temporalmente."}))))

(api.macros/defendpoint :get "/status"
  "Check AI configuration status."
  :- [:map [:configured? :boolean]]
  []
  {:configured? (boolean (System/getenv "MB_LLM_ANTHROPIC_API_KEY"))})

(def routes
  "LW AI routes."
  (api.macros/ns-handler *ns*))
