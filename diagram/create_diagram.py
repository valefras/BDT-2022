from diagrams import Cluster, Diagram
from diagrams.onprem.analytics import Spark
from diagrams.onprem.compute import Server
from diagrams.onprem.database import MySQL
from diagrams.onprem.inmemory import Redis
from diagrams.aws.ml import DeepLearningAmis
from diagrams.programming.framework import Vue
from diagrams.programming.language import Python, NodeJS
from diagrams.custom import Custom

with Diagram("Project pipeline", show=False):
    ingress = Python("Numbeo scraping")

    with Cluster("Pre-processing"):
        primary = Custom("Generate missing \ndata", "./pandas-logo.png")
        saveMain = MySQL("Save data")
        sparkProcessing = Spark("Normalize data")
        saveY = MySQL("Save response")
        clus = [
            primary,
            saveMain,
            sparkProcessing, saveY
        ]
        ingress >> primary >> saveMain >> sparkProcessing >> saveY

    with Cluster("Predictive model"):
        lstm = Custom("LSTM predictions", "./pytorch-logo.png")
        preds = MySQL("Save predictions")
        clus2 = [
            lstm,
            preds
        ]
    saveY >> lstm >> preds

    serve_vue = Vue("Serve client")

    with Cluster("Server API"):
        handle = NodeJS("API request")
        red_lookup = Redis("Check Redis")
        db_lookup = MySQL("Check DB")
        clus3 = [
            handle,
            red_lookup,
            db_lookup
        ]

    preds >> serve_vue >> handle >> red_lookup

    red_lookup >> db_lookup
    db_lookup >> red_lookup
    handle << db_lookup
    handle << red_lookup
