(ns breakbox.client
  (:require [clojure.string :refer [upper-case]]
            [breakbox.http :refer :all]))

(defn- config [type protocol port hosts]
  {
    :type     type
    :protocol protocol
    :port     port
    :hosts    hosts
  }
)

(defn service [protocol port & hosts]
  (config :service protocol port (apply vector hosts)))

(defn client [protocol port & hosts]
  (config :client protocol port (apply vector hosts)))

(defn- to-const [keyword]
  (-> keyword
    name
    upper-case
    (.replace "-" "_")))


(defn fault-command [fault-name config type additional-arg-map]
  (conj {
      :name fault-name
      :type (to-const type)
      :direction ((:type config) { :service "IN" :client "OUT" })
      :to_port (:port config)
      :protocol (to-const (:protocol config))
    }
    additional-arg-map)
)



(defn add-fault [fault-name config type & additional-args]
  (doseq [host (:hosts config)]
    (let [url (str "http://" host ":6660")]
      (post url (fault-command fault-name config type (apply hash-map additional-args))))))


(defn reset [config]
  (doseq [host (:hosts config)]
     (let [url (str "http://" host ":6660")]
       (delete url))))