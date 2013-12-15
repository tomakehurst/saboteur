(ns breakbox.client
  (:require [clojure.string :refer [upper-case]]))

(defn service [protocol port & hosts]
  {
    :protocol protocol
    :port     port
    :hosts    (apply vector hosts)
  }
)

(defn to-const [keyword]
  (-> keyword
    name
    upper-case
    (.replace "-" "_")))


(defn fault-command [fault-name service type & additional-args]
  {
    :name fault-name
    :type (to-const type)
    :direction "IN"
    :to_port (:port service)
    :protocol (to-const (:protocol service))
  }
)