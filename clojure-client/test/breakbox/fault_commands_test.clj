(ns breakbox.fault_commands_test
  (:require [clojure.test :refer :all]
            [breakbox.client :refer :all]
            [midje.sweet :refer :all]))

(def test-service (service :tcp 3000 "host1.myapp.com" "host2.myapp.com"))

(def test-client (client :tcp 8888 "clienthost1"))

(fact "correctly produces network failure fault for a service"
  (fault-command "my-service-network-failure" test-service :network-failure {}) => {
    :name "my-service-network-failure"
    :type "NETWORK_FAILURE"
    :direction "IN"
    :to_port 3000
    :protocol "TCP"
  }
)

(fact "correctly produces network firewall timeout fault for a service"
  (fault-command "a-firewall-timeout" test-service :firewall-timeout {:timeout 12} ) => {
    :name "a-firewall-timeout"
    :type "FIREWALL_TIMEOUT"
    :direction "IN"
    :to_port 3000
    :protocol "TCP"
    :timeout 12
    }
)

(fact "correctly produces network failure fault for a service"
  (fault-command "my-client-service-failure" test-client :service-failure {}) => {
    :name "my-client-service-failure"
    :type "SERVICE_FAILURE"
    :direction "OUT"
    :to_port 8888
    :protocol "TCP"
  }
)