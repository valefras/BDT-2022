from sklearn.preprocessing import StandardScaler, MinMaxScaler
import json
import pandas as pd
import torch
import torch.nn as nn
from torch.autograd import Variable
import matplotlib.pyplot as plt
import numpy as np
from .database_setup import connect, drop_city
plt.style.use('ggplot')
mm = MinMaxScaler()
ss = StandardScaler()


class LSTM1(nn.Module):
    def __init__(self, num_classes, input_size, hidden_size, num_layers, seq_length):
        super(LSTM1, self).__init__()
        self.num_classes = num_classes
        self.num_layers = num_layers
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.seq_length = seq_length

        self.lstm = nn.LSTM(input_size=input_size, hidden_size=hidden_size,
                            num_layers=num_layers, batch_first=True)
        self.fc_1 = nn.Linear(hidden_size, 128)
        self.fc = nn.Linear(128, num_classes)

        self.relu = nn.ReLU()

    def forward(self, x):
        h_0 = Variable(torch.zeros(self.num_layers, x.size(0),
                                   self.hidden_size))  # hidden state
        c_0 = Variable(torch.zeros(self.num_layers, x.size(0),
                                   self.hidden_size))  # internal state
        # lstm with input, hidden, and internal state
        output, (hn, cn) = self.lstm(x, (h_0, c_0))
        # reshaping the data for Dense layer next
        hn = hn.view(-1, self.hidden_size)
        out = self.relu(hn)
        out = self.fc_1(out)
        out = self.relu(out)
        out = self.fc(out)
        return out


def train_LSTM(df_train):
    print("Starting LSTM predictions...")
    cities = df_train.city.unique()
    years = df_train.year.unique()
    conn = connect()
    for city in cities:
        df = df_train[df_train['city'] == city]
        if df.shape[0] < len(years):
            drop_city((city,))
        else:
            df = df.sort_values('year')
            y_df = df.iloc[2:, -1].values
            df_to_predict = df.iloc[-2:, :]
            df_to_predict_main = df.iloc[-2:, :]
            df_to_predict_main.drop(["y"], axis=1, inplace=True)
            df_to_predict.drop(["city", "country", "y"], axis=1, inplace=True)
            df.drop(["city", "country", "y"], axis=1, inplace=True)
            df = df.iloc[:-2, :]
            df = df.assign(y=y_df)
            X = df.iloc[:, :-1]
            y = df.iloc[:, -1:]

            X_ss = ss.fit_transform(X)
            # X_ss = np.array([X.iloc[i,:].values for i in range(X.shape[0])])
            y_mm = mm.fit_transform(y)
            X_train = X_ss
            y_train = y_mm
            X_train_tensors = Variable(torch.Tensor(X_train))

            y_train_tensors = Variable(torch.Tensor(y_train))
            # reshaping to rows, timestamps, features

            X_train_tensors_final = torch.reshape(
                X_train_tensors, (X_train_tensors.shape[0], 1, X_train_tensors.shape[1]))

            num_epochs = 500  # 500 epochs
            learning_rate = 0.001  # 0.001 lr

            input_size = 19  # number of features
            hidden_size = 2  # number of features in hidden state
            num_layers = 1  # number of stacked lstm layers

            num_classes = 1  # number of output classes

            lstm1 = LSTM1(num_classes, input_size, hidden_size, num_layers,
                          X_train_tensors_final.shape[1])  # our lstm class

            criterion = torch.nn.MSELoss()    # mean-squared error for regression
            optimizer = torch.optim.Adam(lstm1.parameters(), lr=learning_rate)

            for epoch in range(num_epochs):
                outputs = lstm1.forward(X_train_tensors_final)  # forward pass
                optimizer.zero_grad()  # caluclate the gradient, manually setting to 0

                # obtain the loss function
                loss = criterion(outputs, y_train_tensors)

                loss.backward()  # calculates the loss of the loss function

                optimizer.step()  # improve from loss, i.e backprop
                if epoch % 100 == 0:
                    print("Epoch: %d, loss: %1.5f" % (epoch, loss.item()))

            df_X_ss = ss.fit_transform(df_to_predict)
            # df_X_ss = np.array([df_to_predict.iloc[i,:].values for i in range(df_to_predict.shape[0])])
            df_X_ss = Variable(torch.Tensor(df_X_ss))  # converting to Tensors

            # reshaping the dataset
            df_X_ss = torch.reshape(
                df_X_ss, (df_X_ss.shape[0], 1, df_X_ss.shape[1]))

            train_predict = lstm1(df_X_ss)  # forward pass
            data_predict = train_predict.data.numpy()  # numpy conversion

            data_predict = mm.inverse_transform(
                data_predict)  # reverse transformation
            df_to_predict_main["y"] = data_predict
            df_to_predict_main = df_to_predict_main[[
                'city', 'country', 'year', 'y']]
            year_tmp = df_to_predict_main["year"].values
            for i in range(len(year_tmp)):
                year_tmp[i] = str(int(year_tmp[i]) + 2)
            df_to_predict_main.assign(year=year_tmp)
            df_to_predict_main.to_sql(con=conn, name='predictions',
                                      if_exists='append', index=False)
    db_conn = conn.connect()
    db_conn.close()
