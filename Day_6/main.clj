;; https://kimh.github.io/clojure-by-example/#scope

(ns main
  (:gen-class)
  (:require [clojure.string :as str])
  (:require [clojure.repl :refer :all]))

(defn parse-lines-to-races
  [times distances]
  (map vector
  ;;  (map #(Integer/parseInt %) (str/split (str/replace times "Time:" "") #"\s"))
       (str/split (str/replace times "Time:" "") #"\s")
      ;;  (map #(Integer/parseInt %)  #"\s")))
       (str/split (str/replace distances "Distance:" "")  #"\s")
       ))

;; Read data from a file
(defn input-file-to-race-info
  "Some documentation for my function"
  ([filename]
   (input-file-to-race-info filename false))

  ([filename smoosh_numbers]

   (if (true? smoosh_numbers)
   (println "TODO: NOT IMPLEMENTED")
   (let [lines (-> filename
                   (slurp)
                   (.split "\n"))
         ]
     (parse-lines-to-races (nth lines 0) (nth lines 1))
     ))



    ;;  (doseq
    ;;   [line (-> filename
    ;;             (slurp)
    ;;             (.split "\n"))]
    ;;    (println line))

    ;;  (map vector

   ;;    (doseq [line lines]
;;      (println line)))

;;    (def vale (clojure.string/replace (nth lines 0) "Time: " "")))
;;    (def data (clojure.string/split val #"\s"))
  ;; replace substring "Time:" with "" and split on whitespace
    ;; (def data (map #(clojure.string/split (clojure.string/replace % "Time:" "") #"\s") lines)
   ))

    ;; if smoosh_numbers:
    ;;     times = [int("".join(data[0].replace("Time:", "").split()))]
    ;;     distances = [int("".join(data[1].replace("Distance:", "").split()))]
    ;; else:
    ;;     times = [int(time) for time in data[0].replace("Time:", "").split()]
    ;;     distances = [int(time) for time in data[1].replace("Distance:", "").split()]
    ;; time_and_distance_pairs = zip(times, distances)

(println (input-file-to-race-info "test_input.txt" ))

;; This program displays Hello World
(defn Example []
   ;; The below code declares a integer variable
  (def x 1)

   ;; The below code declares a float variable
  (def y 1.25)

   ;; The below code declares a string variable
  (def str1 "Hello")
  (println (inc x))
  (println x)
  (println y)
  (println str1))


;; (println (doc input-file-to-race-info))