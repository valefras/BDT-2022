import pipeline.ingestion as ingestion
import pipeline.database_setup as DB
#import pandas as pd
import pipeline.train as LSTM


def start():
    DB.create_db()
    DB.create_tables()
    df_final = ingestion.scrape()
    #df_final = pd.read_csv('final_results.csv', sep=",")
    LSTM.train_LSTM(df_final)
    print("Process completed!")

start()