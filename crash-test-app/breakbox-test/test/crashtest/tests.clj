(ns crashtest.tests
  (:require [clojure.test :refer :all]
            [breakbox.client :refer :all]
            [uritemplate-clj.core :refer :all])
  (:use crashtest.core))

(def crash-test-http-dependency (client :tcp 8080 "192.168.2.12"))

(def something-url "http://192.168.2.12:8080/something")

(defn get-something []
  (timed-get {} something-url))

(deftest get-tags-should-not-exceed-5s-under-network-failure
  (add-fault "http-service-network-failure" crash-test-http-dependency :network-failure)
  (wait-for-completion
    (dothreads! get-something :threads 10 :times 100))

  (println (get-timer-names))

  (let [something-snapshot (timer-snapshot "get" something-url)
        percentile95 (to-millis (.get95thPercentile something-snapshot))]
    (is (< percentile95 5000))
    (is (> percentile95 0))))


