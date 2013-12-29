(ns crashtest.core
  (:require [breakbox.client :refer :all]
            [uritemplate-clj.core :refer :all]
            [org.httpkit.client :as http])
  (:import  [com.codahale.metrics MetricRegistry])
  (:import  [java.util.concurrent Executors TimeUnit]))

(def metrics (new MetricRegistry))

(defn dothreads! [f & {thread-count :threads
                       exec-count :times
                       :or {thread-count 1 exec-count 1}}]
  (printf "Running %d times in %d threads\n" exec-count thread-count)
  (let [pool (Executors/newFixedThreadPool thread-count)
        tasks (repeat exec-count f)
        task-futures (.invokeAll pool tasks)]
    task-futures))

(defn wait-for-completion [futures]
  (doseq [fut futures]
    @fut))

(defn metric-name [name & names]
  (MetricRegistry/name name (into-array names)))

(defn create-timer [method uri-template]
  (.timer metrics (metric-name method uri-template)))

(defn get-timer-names []
  (.keySet (.getTimers metrics)))

(defn timer-snapshot [method uri-template]
  (let [timer-name (metric-name method uri-template)]
    (.getSnapshot (get (.getTimers metrics) timer-name))))

(defn to-millis [nanos]
  (.toMillis TimeUnit/NANOSECONDS nanos))

(defn timed-get [options uri-template & uri-params]
  (let [uri (uritemplate uri-template (apply hash-map uri-params))
        timer (create-timer "get" uri-template)
        timer-context (.time timer)
        response @(http/get uri options)]
    (.stop timer-context)
    response))