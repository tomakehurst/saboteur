(ns crashtest.tests
  (:require [clojure.test :refer :all]
            [breakbox.client :refer :all]
            [uritemplate-clj.core :refer :all])
  (:use crashtest.core))

(def crash-test-http-dependency (client :tcp 8080 "192.168.2.12"))

(defn reset-breakbox-fixture [f]
  (reset crash-test-http-dependency)
  (f)
  (reset crash-test-http-dependency))

(use-fixtures :each reset-breakbox-fixture)

(def faulty-resource-url "http://192.168.2.12:8080/no-connect-timeout")

(defn get-faulty-resource []
  (timed-get { :timeout 2000 } faulty-resource-url))



(deftest get-should-not-exceed-1s
  (add-fault "http-service-network-failure" crash-test-http-dependency :network-failure)

  (wait-for-completion
    (dothreads! get-faulty-resource :threads 5 :times 100))

  (let [something-snapshot (timer-snapshot "get" faulty-resource-url)
        percentile95 (to-millis (.get95thPercentile something-snapshot))]
    (is (< percentile95 1000))
    (is (> percentile95 0))))


