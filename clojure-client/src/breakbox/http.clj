(ns breakbox.http
  (:require [org.httpkit.client :as http]
            [clojure.data.json :as json]))

(defn post [url body-map]
  (let [body (json/write-str body-map)]
    (:status @(http/post url { :body body }))))

(defn delete [url]
  (:status @(http/delete url)))