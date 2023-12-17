import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import lightgbm as lm
import pickle
import warnings
warnings.filterwarnings("ignore")

df = pd.read_csv("cars_details_merges.csv")
df.head()

df['body'] = df['bt'].replace({'Hatchback':0,'Hybrids':1,'Luxury Vehicles':2,'Minivans':3,'MUV':4,'Pickup Trucks':5,'Sedan':6,'SUV':7,'Wagon':8})
df['fuel'] = df['ft'].replace({'CNG':0,'Diesel':1,'Electric':2,'LPG':3,'Petrol':4})
df['colour'] = df['color'].replace({'Black':0,'Blue':1,'Brown':2,'Gold':3,'Green':4,'Grey':5,'Maroon':6,'Orange':7,'Other':8,'Red':9,'Silver':10,'White':11,'Yellow':12})

category_mappings = {}
categorical_columns = ['brand', 'model', 'variant', 'State/UT']
le = LabelEncoder()
for col in categorical_columns:
    df[col + 'LE'] = le.fit_transform(df[col])
    category_mappings[col] = dict(zip(le.classes_, le.transform(le.classes_)))

df.drop(['brand', 'model', 'variant', 'State/UT'],axis=1,inplace=True)
df.drop(['bt','ft','color'],axis=1,inplace=True)

x = df.drop(['price'],axis = 1)
y = df['price']

x_train,x_test,y_train,y_test = train_test_split(x,y,test_size = 0.1,random_state = 42)

lgb = lm.LGBMRegressor(force_row_wise=True, subsample = 1.0,n_estimators= 300,min_child_weight= 1,max_depth=10,num_leaves=64,learning_rate= 0.1,boosting_type='gbdt',colsample_bytree= 1.0).fit(x_train,y_train)

#Ayush's Car Prediction
input_data = [2016,180000,1,0,1,1,1,0,0,0,0,0,1,1,0,1,0,1,1,1,1,1,0,0,1,1,1,1,1,1,0,0,0,0,0,1,1,0,0,0,1,0,1,1,0,1,0,6,1,11,23,155,1542,11]
input_data = np.array(input_data).reshape(1, -1)
output = lgb.predict(input_data)[0]
print('Predicted Price : ', output)

pickle.dump(lgb,open('model.pkl','wb'))
pickle.dump(category_mappings,open('mappings.pkl','wb'))