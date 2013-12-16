(ns breakbox.http
  (:require [org.httpkit.client :as http]))

(defn post [url body]
  (:status @(http/post url { :body body })))

(defn delete [url]
  (:status @(http/delete url)))