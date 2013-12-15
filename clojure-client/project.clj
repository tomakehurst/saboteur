(defproject clojure-client "0.1.0-SNAPSHOT"
  :description "A Clojure client for Breakbox"
  :url "https://github.com/tomakehurst/breakbox"
  :dependencies [[org.clojure/clojure "1.5.1"]
  	[http-kit "2.1.13"]]
  :profiles {:dev { :dependencies [[midje "1.6.0"]]
                    :plugins [[lein-midje "3.1.3"]]}})
