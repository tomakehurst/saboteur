(ns breakbox.client
  (:require [clojure.string :refer [upper-case]]
            [breakbox.http :refer :all]))

(defn service [protocol port & hosts]
  {
    :protocol protocol
    :port     port
    :hosts    (apply vector hosts)
  }
)

(defn- to-const [keyword]
  (-> keyword
    name
    upper-case
    (.replace "-" "_")))


(defn fault-command [fault-name service type additional-arg-map]
  (conj {
      :name fault-name
      :type (to-const type)
      :direction "IN"
      :to_port (:port service)
      :protocol (to-const (:protocol service))
    }
    additional-arg-map)
)


(defn add-fault [fault-name service type & additional-args]
  (doseq [host (:hosts service)]
    (let [url (str "http://" host ":6660")]
      (post url (fault-command fault-name service type (apply hash-map additional-args))))))


(defn reset [service]
  (doseq [host (:hosts service)]
     (let [url (str "http://" host ":6660")]
       (delete url))))