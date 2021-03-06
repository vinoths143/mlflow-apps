# Copyright 2018 Databricks, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import re
import sys
import pandas

# Downloads the diamonds dataset into the provided folder path.
# Converts categorical values into numerical values and splits the data into training/testing sets.
def download_diamonds(temp_folder_path):

    #Downloading csv file from ggplot2's hosted dataset on github.
    url = "https://raw.githubusercontent.com/tidyverse/ggplot2/4c678917/data-raw/diamonds.csv"
    print("Downloading diamonds csv file to %s..." % temp_folder_path)

    pd_df = pandas.read_csv(url)
    print("Downloaded diamonds csv file.")

    # Conversion of qualitative values to quantitative values. For diamonds only.
    pd_df['cut'] = pd_df['cut'].replace({'Fair':0, 'Good':1, 
                                                    'Very Good':2, 'Premium':3, 'Ideal':4})
    pd_df['color'] = pd_df['color'].replace({'J':0, 'I':1, 
                                                        'H':2, 'G':3, 'F':4, 'E':5, 'D':6})
    pd_df['clarity'] = pd_df['clarity'].replace({'I1':0, 
                            'SI1':1, 'SI2':2, 'VS1':3, 'VS2':4, 'VVS1':5, 'VVS2':6, 'IF':7})

    pd_df.rename(columns=lambda x: re.sub(r'[^\w]', '', x), inplace=True)
    # Shuffling the dataset for more accurate training and testing results.
    pd_df = pd_df.sample(frac=1).reset_index(drop=True)
    # Splitting the data up so that 80% of the data is training data, 20% testing data.
    training_data = pd_df[:int(pd_df.shape[0]*.8)]
    testing_data = pd_df[int(pd_df.shape[0]*.8):]
    print("Creating diamonds dataset parquet files...")
    with open(os.path.join(temp_folder_path, "train_diamonds.parquet"), 'w'):
        training_data.to_parquet(os.path.join(temp_folder_path, "train_diamonds.parquet"))
    with open(os.path.join(temp_folder_path, "test_diamonds.parquet"), 'w'):
        testing_data.to_parquet(os.path.join(temp_folder_path, "test_diamonds.parquet"))
    print("Diamonds dataset parquet files created.")

    # Saving a CSV file of the dataset for predicting purposes.
    csv_predict = pd_df.drop(["price"], 1)
    # The number of data points we want to predict on when calling mlflow pyfunc predict.
    num_pred = 20
    csv_predict[:num_pred].to_csv(os.path.join(temp_folder_path, "diamonds.csv"), index=False)
    # This CSV file contains the price of the tested diamonds.
    # Predictions can be compared with these actual values.
    pd_df["price"][:num_pred].to_csv(os.path.join(temp_folder_path, "diamond_prices.csv"),
                                   index=False)

    return pd_df

if __name__ == '__main__':
    download_diamonds(sys.argv[1])
