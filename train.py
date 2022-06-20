from sklearn.preprocessing import StandardScaler, MinMaxScaler
import json
import pandas as pd
import torch  # pytorch
import torch.nn as nn
from torch.autograd import Variable
import matplotlib.pyplot as plt
plt.style.use('ggplot')
mm = MinMaxScaler()
ss = StandardScaler()

with open('new_scraped_results.txt') as f:
    to_insert = json.loads(f.read())

cols = {
    "year": [],
    "cost_of_living_index": [],
    "rent_index": [],
    "groceries_index": [],
    "restaurant_price_index": [],
    "local_ppi_index": [],
    "crime_index": [],
    "safety_index": [],
    "qol_index": [],
    "ppi_index": [],
    "health_care_index": [],
    "traffic_commute_index": [],
    "pollution_index": [],
    "climate_index": [],
    "gross_rental_yield_centre": [],
    "gross_rental_yield_out": [],
    "price_to_rent_centre": [],
    "price_to_rent_out": [],
    "affordability_index": [],
    "y": []
}

years = set()


class LSTM1(nn.Module):
    def __init__(self, num_classes, input_size, hidden_size, num_layers, seq_length):
        super(LSTM1, self).__init__()
        self.num_classes = num_classes  # number of classes
        self.num_layers = num_layers  # number of layers
        self.input_size = input_size  # input size
        self.hidden_size = hidden_size  # hidden state
        self.seq_length = seq_length  # sequence length

        self.lstm = nn.LSTM(input_size=input_size, hidden_size=hidden_size,
                            num_layers=num_layers, batch_first=True)  # lstm
        self.fc_1 = nn.Linear(hidden_size, 128)  # fully connected 1
        self.fc = nn.Linear(128, num_classes)  # fully connected last layer

        self.relu = nn.ReLU()

    def forward(self, x):
        h_0 = Variable(torch.zeros(self.num_layers, x.size(0),
                                   self.hidden_size))  # hidden state
        c_0 = Variable(torch.zeros(self.num_layers, x.size(0),
                                   self.hidden_size))  # internal state
        # Propagate input through LSTM
        # lstm with input, hidden, and internal state
        output, (hn, cn) = self.lstm(x, (h_0, c_0))
        # reshaping the data for Dense layer next
        hn = hn.view(-1, self.hidden_size)
        out = self.relu(hn)
        out = self.fc_1(out)  # first Dense
        out = self.relu(out)  # relu
        out = self.fc(out)  # Final Output
        return out


for city in to_insert:
    for year in [*city["metrics"]]:
        years.add(year)
        cols["year"].append(year)
        for key in [*cols][1:]:
            if key == "y":
                if str(int(year) + 2) in city["metrics"]:
                    cols[key].append(city["metrics"][str(int(year) + 2)][key])
                else:
                    cols[key].append(0)
            else:
                cols[key].append(city["metrics"][year][key])

    df = pd.DataFrame(cols)
    df = df.sort_values('year')
    df = df.set_index('year')
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1:]
    X_ss = ss.fit_transform(X)
    y_mm = mm.fit_transform(y)

    X_train = X_ss[:-2, :]
    X_test = X_ss[-2:, :]

    y_train = y_mm[:-2]
    y_test = y_mm[-2:]

    X_train_tensors = Variable(torch.Tensor(X_train))
    X_test_tensors = Variable(torch.Tensor(X_test))

    y_train_tensors = Variable(torch.Tensor(y_train))
    y_test_tensors = Variable(torch.Tensor(y_test))

    # reshaping to rows, timestamps, features

    X_train_tensors_final = torch.reshape(
        X_train_tensors, (X_train_tensors.shape[0], 1, X_train_tensors.shape[1]))
    X_test_tensors_final = torch.reshape(
        X_test_tensors, (X_test_tensors.shape[0], 1, X_test_tensors.shape[1]))

    num_epochs = 500  # 500 epochs
    learning_rate = 0.001  # 0.001 lr

    input_size = 18  # number of features
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

    df_X_ss = ss.transform(df.iloc[:, :-1])  # old transformers
    df_y_mm = mm.transform(df.iloc[:, -1:])  # old transformers

    df_X_ss = Variable(torch.Tensor(df_X_ss))  # converting to Tensors
    df_y_mm = Variable(torch.Tensor(df_y_mm))
    # reshaping the dataset
    df_X_ss = torch.reshape(df_X_ss, (df_X_ss.shape[0], 1, df_X_ss.shape[1]))

    train_predict = lstm1(df_X_ss)  # forward pass
    data_predict = train_predict.data.numpy()  # numpy conversion
    dataY_plot = df_y_mm.data.numpy()

    data_predict = mm.inverse_transform(data_predict)  # reverse transformation
    dataY_plot = mm.inverse_transform(dataY_plot)
    plt.figure(figsize=(10, 6))  # plotting
    # size of the training set
    plt.axvline(x=len(year)-1, c='r', linestyle='--')
    print(dataY_plot)
    print(data_predict)
    plt.plot(dataY_plot, label='Actual Data')  # actual plot
    plt.plot(data_predict, label='Predicted Data')  # predicted plot
    plt.title('Time-Series Prediction')
    plt.legend()
    plt.show()
    cols = {
        "year": [],
        "cost_of_living_index": [],
        "rent_index": [],
        "groceries_index": [],
        "restaurant_price_index": [],
        "local_ppi_index": [],
        "crime_index": [],
        "safety_index": [],
        "qol_index": [],
        "ppi_index": [],
        "health_care_index": [],
        "traffic_commute_index": [],
        "pollution_index": [],
        "climate_index": [],
        "gross_rental_yield_centre": [],
        "gross_rental_yield_out": [],
        "price_to_rent_centre": [],
        "price_to_rent_out": [],
        "affordability_index": [],
        "y": []
    }
