import streamlit as st
import joblib
import pandas as pd
import numpy as np

# Load the model and scaler
model = joblib.load('fraud_detection_model.pkl')
scaler = joblib.load('scaler.pkl')

# Streamlit UI
st.title('Fraud Detection System')
st.write('Enter transaction details to check for fraud:')

# Input fields
cc_num = st.number_input('Credit Card Number', value=0)
merchant = st.text_input('Merchant', value='fraud_Kirlin and Sons')
category = st.selectbox('Category', ['personal_care', 'health_fitness', 'misc_pos', 'travel', 'kids_pets', 'food_dining', 'shopping_pos', 'entertainment', 'home'])
amt = st.number_input('Amount', value=0.0)
city_pop = st.number_input('City Population', value=0)
unix_time = st.number_input('Unix Time', value=0)
lat = st.number_input('Latitude', value=0.0)
long = st.number_input('Longitude', value=0.0)
merch_lat = st.number_input('Merchant Latitude', value=0.0)
merch_long = st.number_input('Merchant Longitude', value=0.0)

# Predict button
if st.button('Check for Fraud'):
    # Create input array
    input_data = pd.DataFrame({
        'cc_num': [cc_num],
        'merchant': [merchant],
        'category': [category],
        'amt': [amt],
        'city_pop': [city_pop],
        'unix_time': [unix_time],
        'lat': [lat],
        'long': [long],
        'merch_lat': [merch_lat],
        'merch_long': [merch_long]
    })

    # Encode categorical variables
    input_data = pd.get_dummies(input_data, columns=['merchant', 'category'], drop_first=True)

    # Ensure all columns are present (add missing columns with 0)
    train_columns = joblib.load('train_columns.pkl')  # Save train columns during training
    for col in train_columns:
        if col not in input_data.columns:
            input_data[col] = 0

    # Reorder columns to match training data
    input_data = input_data[train_columns]

    # Scale the input data
    input_data_scaled = scaler.transform(input_data)

    # Make prediction
    prediction = model.predict(input_data_scaled)

    # Display result
    if prediction[0] == 1:
        st.error('Fraudulent Transaction Detected!')
    else:
        st.success('Transaction is Safe.')