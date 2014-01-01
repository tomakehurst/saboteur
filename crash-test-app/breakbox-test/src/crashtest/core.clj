(ns crashtest.core
  (:require [breakbox.client :as breakbox]
            [uritemplate-clj.core :refer :all]
            [org.httpkit.client :as http]
            [clojure.test :refer :all])
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

(defn convert-units [nanos unit]
  (case unit
    :seconds      (.toSeconds TimeUnit/NANOSECONDS nanos)
    :milliseconds (.toMillis TimeUnit/NANOSECONDS nanos)
    :microseconds (.toMicros TimeUnit/NANOSECONDS nanos)
    nanos))

(defn timed-get [options uri-template & uri-params]
  (let [uri (uritemplate uri-template (apply hash-map uri-params))
        timer (create-timer "get" uri-template)
        timer-context (.time timer)
        response @(http/get uri options)]
    (.stop timer-context)
    response))

(defn reset-breakbox [config]
  (fn [f]
    (breakbox/reset config)
    (f)
    (breakbox/reset config)))

(defn- percentile-str [percentile]
  (let [suffix (case (mod percentile 10)
                 1 "st"
                 2 "nd"
                 3 "rd"
                 "th")]
    (str percentile suffix " percentile")))

(defn assert-percentile [quantile snapshot operator value unit]
  (let [percentile-val (convert-units (.getValue snapshot (double (/ quantile 100))) unit)]
    (if (operator percentile-val value)
      (do-report { :type :pass, :message "OK", :expected value, :actual percentile-val })
      (do-report { :type :fail,
                   :message (percentile-str quantile),
                   :expected (str value " " (name unit)),
                   :actual (str percentile-val " " (name unit)) }))))