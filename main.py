import ingestion
import database_setup as DB
import pandas as pd
import train as LSTM


def start():
    DB.create_db()
    DB.create_tables()
    df_final = ingestion.scrape()
    #df_final.to_csv("final_results.csv", sep=',')
    #df_final = pd.read_csv('final_results.csv', sep=",")
    LSTM.train_LSTM(df_final)
    print("Process completed!")

start()