import pipeline.ingestion as ingestion
import pipeline.database_setup as DB
import pipeline.train as LSTM


def start():
    DB.create_db()
    DB.create_tables()
    df_final = ingestion.scrape()
    LSTM.train_LSTM(df_final)
    print("Process completed!")

start()