(ns breakbox.client-test
  (:require [breakbox.client :refer :all]
            [breakbox.http :refer :all]
            [clojure.data.json :as json]
            [midje.sweet :refer :all]))

(def test-service (service :tcp 3000 "host1.myapp.com" "host2.myapp.com"))

(fact "adds fault to all hosts"
  (add-fault "total-network-failure" test-service :network-failure) => nil
  (provided
    (post "http://host1.myapp.com:6660" anything) => 201 :times 1)
  (provided
    (post "http://host2.myapp.com:6660" anything) => 201 :times 1))


(fact "resets all hosts"
  (reset test-service) => nil
  (provided
    (delete "http://host1.myapp.com:6660") => 200 :times 1)
  (provided
    (delete "http://host2.myapp.com:6660") => 200 :times 1))