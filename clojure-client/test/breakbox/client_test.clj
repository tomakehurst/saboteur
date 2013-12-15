(ns breakbox.client_test
  (:require [clojure.test :refer :all]
            [breakbox.client :refer :all]
            [midje.sweet :refer :all]))

(def test-service (service :tcp 3000 "host1.myapp.com" "host2.myapp.com"))

(fact "correctly produces network failure fault"
  (fault-command "my-service-network-failure" test-service :network-failure) => {
    :name "my-service-network-failure"
    :type "NETWORK_FAILURE"
    :direction "IN"
    :to_port 3000
    :protocol "TCP"
  }
)

(fact "correctly produces network firewall timeout fault"
  (fault-command "a-firewall-timeout" test-service :firewall-timeout :timeout 12 ) => {
    :name "a-firewall-timeout"
    :type "FIREWALL_TIMEOUT"
    :direction "IN"
    :to_port 3000
    :protocol "TCP"
    :timeout 12
    }
  )
