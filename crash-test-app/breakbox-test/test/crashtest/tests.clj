(ns crashtest.tests
  (:require [clojure.test :refer :all]
            [breakbox.client :as breakbox]
            [uritemplate-clj.core :refer :all])
  (:use crashtest.core))

(def crash-test-http-dependency (breakbox/client :tcp 8080 "192.168.2.12"))
(use-fixtures :each (reset-breakbox crash-test-http-dependency))

(def faulty-resource-url "http://192.168.2.12:8080/no-connect-timeout")
(defn get-faulty-resource []
  (timed-get { :timeout 2000 } faulty-resource-url))


(deftest get-should-not-exceed-1s
  (breakbox/add-fault "http-service-network-failure" crash-test-http-dependency :network-failure)

  (wait-for-completion (dothreads! get-faulty-resource :threads 5 :times 100))

  (let [faulty-resource-timer (timer-snapshot "get" faulty-resource-url)]
    (assert-percentile 50 faulty-resource-timer < 700)
    (assert-percentile 95 faulty-resource-timer < 1000)
    (assert-percentile 95 faulty-resource-timer > 0)))


