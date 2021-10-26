# -*- coding: utf-8 -*-
"""Predicting house prices.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1dKk1oNDyHu-klupCNj2cEGdRuy28plRn

importing required libraries
"""

# Commented out IPython magic to ensure Python compatibility.
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
# %matplotlib inline

color = sns.color_palette()
sns.set_style('darkgrid')

from scipy import stats
from scipy.stats import norm, skew #for some statistics

import hvplot.pandas
import holoviews as hv

# setting bokeh as backend
hv.extension('bokeh')

# going to use show() to open plot in browser
from bokeh.plotting import show

## loading the training and test data from kaggle

test_df=pd.read_csv('test.csv')
train_df=pd.read_csv('train.csv')

train_df.head()

test_df.head()

#Save the 'Id' column
train_ID = train_df['Id']
test_ID = test_df['Id']

"""### Exploratory Data Analysis

analyzing the data found in the saleprice column
"""

sns.distplot(train_df['SalePrice'] , fit=norm)

"""since the target variable is skewed to the left we are going to log transform the data to achieve a normal distribution"""

train_df['SalePrice'] = np.log(train_df['SalePrice'])

#Check the new distribution to see the normalized data
sns.distplot(train_df['SalePrice'] , fit=norm);

"""Looking at the relationship between SalePrice and certain features

Relationship between SalePrice and OverallQual
"""

fig = plt.figure(figsize= (10,6))
sns.boxplot(x = "OverallQual", y = "SalePrice", data = train_df)
plt.show()

"""Relationship between Saleprice and Neigbhourhood"""

fig = plt.figure(figsize= (10,6))
sns.boxplot(x = "Neighborhood", y = "SalePrice", data = train_df)
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()

"""Correlation matrix"""

# Create correlation matrix
corr_matrix = train_df.corr().abs()

fig = plt.figure(figsize= (30,30))
sns.heatmap(corr_matrix, annot=True, vmax=1, cmap='Blues', square=False)

"""### Feature Engineering

joining the test and train data where the saleprice column has been dropped to make it easier to work with for cleaning the data
"""

ntrain = train_df.shape[0]
ntest = test_df.shape[0]

y_train = train_df[['Id','SalePrice']]
all_data = pd.concat((train_df, test_df)).reset_index(drop=True)
all_data.drop(['SalePrice'], axis=1, inplace=True)
print("all_data size is : {}".format(all_data.shape))

y_train.head()

all_data.head()

"""#### Data Cleaning"""

#assessing all the columns in the data that have missing data 
forever=round(all_data.isnull().mean()*100,2)
forever = forever[forever > 0]

forever

forever = forever.sort_values(ascending=False)

f, ax = plt.subplots(figsize=(15, 12))
plt.xticks(rotation='90')
sns.barplot(x=forever.index, y=forever,palette='Blues')
plt.xlabel('Features', fontsize=15)
plt.ylabel('missing values', fontsize=15)
plt.title('missing data by feature', fontsize=15)

plt.savefig('missingdatabyfeatures.jpg')

"""Handling the missing data for the missing data columns """

#top 5 missing data columns
all_data["PoolQC"] = all_data["PoolQC"].fillna("None")
all_data["MiscFeature"] = all_data["MiscFeature"].fillna("None")
all_data["Alley"] = all_data["Alley"].fillna("None")
all_data["Fence"] = all_data["Fence"].fillna("None")
all_data["FireplaceQu"] = all_data["FireplaceQu"].fillna("None")
all_data["GarageFinish"] = all_data["GarageFinish"].fillna("None")
all_data["GarageQual"] = all_data["GarageQual"].fillna("None")
all_data["GarageCond"] = all_data["GarageCond"].fillna("None")
all_data["GarageType"] = all_data["GarageType"].fillna("None")

for col in ['BsmtExposure', 'BsmtCond', 'BsmtQual', 'BsmtFinType1','BsmtFinType2']:
    all_data[col] = all_data[col].fillna('None')

for col in ('BsmtFinSF1', 'BsmtFinSF2', 'BsmtUnfSF','TotalBsmtSF', 'BsmtFullBath', 'BsmtHalfBath'):
    all_data[col] = all_data[col].fillna(0)
for col in ('GarageYrBlt', 'GarageArea', 'GarageCars'):
    all_data[col] = all_data[col].fillna(0)

# Group the by neighborhoods, and fill in missing value by the median LotFrontage of the neighborhood
all_data['LotFrontage'] = all_data.groupby('Neighborhood')['LotFrontage'].transform(lambda x: x.fillna(x.median()))

all_data["MasVnrType"] = all_data["MasVnrType"].fillna("None")
all_data["MasVnrArea"] = all_data["MasVnrArea"].fillna(0)

all_data['MSZoning'] = all_data['MSZoning'].fillna(all_data['MSZoning'].mode()[0])

all_data = all_data.drop(['Utilities'], axis=1)
all_data["Functional"] = all_data["Functional"].fillna("Typ")
all_data['Electrical'] = all_data['Electrical'].fillna(all_data['Electrical'].mode()[0])
all_data['KitchenQual'] = all_data['KitchenQual'].fillna(all_data['KitchenQual'].mode()[0])
all_data['Exterior1st'] = all_data['Exterior1st'].fillna(all_data['Exterior1st'].mode()[0])
all_data['Exterior2nd'] = all_data['Exterior2nd'].fillna(all_data['Exterior2nd'].mode()[0])
all_data['SaleType'] = all_data['SaleType'].fillna(all_data['SaleType'].mode()[0])

#MSSubClass=The building class
all_data['MSSubClass'] = all_data['MSSubClass'].apply(str)


#Changing OverallCond into a categorical variable
all_data['OverallCond'] = all_data['OverallCond'].astype(str)


#Year and month sold are transformed into categorical features.
all_data['YrSold'] = all_data['YrSold'].astype(str)
all_data['MoSold'] = all_data['MoSold'].astype(str)

all_data.head()

"""Fixing Skewed data """

# Fetch all numeric features
numeric_dtypes = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
numeric = []
for i in all_data.columns:
    if all_data[i].dtype in numeric_dtypes:
        numeric.append(i)

# Create box plots for all numeric features
#sns.set_style("white")
f, ax = plt.subplots(figsize=(10, 6))
ax.set_xscale("log")
ax = sns.boxplot(data=all_data[numeric] , orient="h", palette="Blues")
ax.xaxis.grid(False)
ax.set(ylabel="Feature names")
ax.set(xlabel="Numeric values")
ax.set(title="Numeric Distribution of Features")
#sns.despine(trim=True, left=True)

fig = plt.figure(figsize= (10,6))
sns.boxplot(x = "Neighborhood", y = "SalePrice", data = train_df)
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()

"""Dealing with categorical variables in the data """

## Utilizing dummy variables for the categorical variables
#all_data = pd.get_dummies(all_data).reset_index(drop=True)

"""decided to use just the numerical variables for the modelling"""

all_data=all_data._get_numeric_data().reset_index(drop=True)

all_data.head()

#data without the y variable
train_labels = all_data[:ntrain]
test_labels = all_data[ntrain:]

y=y_train.drop(['Id'], axis=1)

from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(train_labels, y_train, test_size=0.3, random_state=42)

from sklearn import metrics
from sklearn.model_selection import cross_val_score

def cross_val(model):
    pred = cross_val_score(model, train_labels, y, cv=10)
    return pred.mean()

def print_evaluate(true, predicted):  
    mae = metrics.mean_absolute_error(true, predicted)
    mse = metrics.mean_squared_error(true, predicted)
    rmse = np.sqrt(metrics.mean_squared_error(true, predicted))
    r2_square = metrics.r2_score(true, predicted)
    print('MAE:', mae)
    print('MSE:', mse)
    print('RMSE:', rmse)
    print('R2 Square', r2_square)
    print('__________________________________')
    
def evaluate(true, predicted):
    mae = metrics.mean_absolute_error(true, predicted)
    mse = metrics.mean_squared_error(true, predicted)
    rmse = np.sqrt(metrics.mean_squared_error(true, predicted))
    r2_square = metrics.r2_score(true, predicted)
    return mae, mse, rmse, r2_square

"""# Modelling

Linear Regression

Preparing data for linear regression
"""

from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

pipeline = Pipeline([
    ('std_scalar', StandardScaler())
])

X_train = pipeline.fit_transform(X_train)
X_test = pipeline.transform(X_test)

from sklearn.linear_model import LinearRegression

lin_reg = LinearRegression(normalize=True)
lin_reg.fit(X_train,y_train)

pred = lin_reg.predict(X_test)

# print the intercept
print(lin_reg.intercept_)

ind = range(len(y_test))

y_test = np.array(y_test)

plot = pd.DataFrame({'True Values': y_test[:,0], 'Predicted Values': pred[:, 0]}, index = ind).hvplot.scatter(x='True Values', y='Predicted Values')

show(hv.render(plot))

test_pred = lin_reg.predict(X_test)
train_pred = lin_reg.predict(X_train)

print('Test set evaluation:\n_____________________________________')
print_evaluate(y_test, test_pred)
print('Train set evaluation:\n_____________________________________')
print_evaluate(y_train, train_pred)

results_df = pd.DataFrame(data=[["Linear Regression", *evaluate(y_test, test_pred) , cross_val(LinearRegression())]], 
                          columns=['Model', 'MAE', 'MSE', 'RMSE', 'R2 Square', "Cross Validation"])
results_df

"""Random Forest Regression"""

from sklearn.metrics import mean_squared_error
from sklearn.ensemble import RandomForestRegressor
from sklearn import preprocessing
from sklearn.model_selection import cross_validate

from sklearn.ensemble import RandomForestRegressor

rf_reg = RandomForestRegressor(n_estimators=1000)
rf_reg.fit(X_train, y_train)

test_pred = rf_reg.predict(X_test)
train_pred = rf_reg.predict(X_train)

print('Test set evaluation:\n_____________________________________')
print_evaluate(y_test, test_pred)

print('Train set evaluation:\n_____________________________________')
print_evaluate(y_train, train_pred)

results_df_2 = pd.DataFrame(data=[["Random Forest Regressor", *evaluate(y_test, test_pred), 0]], 
                            columns=['Model', 'MAE', 'MSE', 'RMSE', 'R2 Square', 'Cross Validation'])
results_df = results_df.append(results_df_2, ignore_index=True)

results_df.head()

"""Artificial Neural Networks"""

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, Dense, Activation, Dropout
from tensorflow.keras.optimizers import Adam

import numpy as np
from keras.models import Sequential
from keras.layers import Dense
from keras.wrappers.scikit_learn import KerasRegressor

seed = 7
np.random.seed(seed)

X_train = np.array(X_train)
X_test = np.array(X_test)
y_train = np.array(y_train)
y_test = np.array(y_test)


model = Sequential()

model.add(Dense(X_train.shape[1], activation='relu'))
model.add(Dense(32, activation='relu'))
# model.add(Dropout(0.2))

model.add(Dense(64, activation='relu'))
# model.add(Dropout(0.2))

model.add(Dense(128, activation='relu'))
# model.add(Dropout(0.2))

model.add(Dense(512, activation='relu'))
model.add(Dropout(0.1))
model.add(Dense(1))

model.compile(optimizer=Adam(0.00001), loss='mse')

r = model.fit(X_train, y_train,
              validation_data=(X_test,y_test),
              batch_size=1,
              epochs=100)

pd.DataFrame({'True Values': y_test[:,0], 'Predicted Values': pred[:, 0]}, index = ind).hvplot.scatter(x='True Values', y='Predicted Values')

pd.DataFrame(r.history)

plot=pd.DataFrame(r.history).hvplot.line(y=['loss', 'val_loss'])

show(hv.render(plot))

test_pred = model.predict(X_test)
train_pred = model.predict(X_train)

print('Test set evaluation:\n_____________________________________')
print_evaluate(y_test[:,0], test_pred)

print('Train set evaluation:\n_____________________________________')
print_evaluate(y_train[:,0], train_pred)

results_df_3 = pd.DataFrame(data=[["Artficial Neural Network", *evaluate(y_test[:,0], test_pred), 0]], 
                            columns=['Model', 'MAE', 'MSE', 'RMSE', 'R2 Square', 'Cross Validation'])
results_df = results_df.append(results_df_3, ignore_index=True)
results_df

results_df.set_index('Model', inplace=True)
results_df['R2 Square'].plot(kind='barh', figsize=(12, 8))