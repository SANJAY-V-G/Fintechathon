import streamlit as st
import joblib
import numpy as np

# Load the model and scaler
model = joblib.load('fraud_detection_model.pkl')
scaler = joblib.load('scaler.pkl')

# Streamlit UI
st.title('Fraud Detection System')
st.write('Enter transaction details to check for fraud:')

# Input fields
transaction_type = st.selectbox('Transaction Type', ['CASH_IN', 'CASH_OUT', 'DEBIT', 'PAYMENT', 'TRANSFER'])
amount = st.number_input('Amount', value=0.0)
oldbalanceOrg = st.number_input('Old Balance Origin', value=0.0)
newbalanceOrig = st.number_input('New Balance Origin', value=0.0)
oldbalanceDest = st.number_input('Old Balance Destination', value=0.0)
newbalanceDest = st.number_input('New Balance Destination', value=0.0)

# Encode transaction type
transaction_type_encoded = {
    'CASH_IN': [0, 0, 0, 0],
    'CASH_OUT': [1, 0, 0, 0],
    'DEBIT': [0, 1, 0, 0],
    'PAYMENT': [0, 0, 1, 0],
    'TRANSFER': [0, 0, 0, 1]
}

# Predict button
if st.button('Check for Fraud'):
    # Create input array
    input_data = np.array([[amount, oldbalanceOrg, newbalanceOrig, oldbalanceDest, newbalanceDest] + transaction_type_encoded[transaction_type]])
    
    # Scale the input data
    input_data_scaled = scaler.transform(input_data)
    
    # Make prediction
    prediction = model.predict(input_data_scaled)
    
    # Display result
    if prediction[0] == 1:
        st.error('Fraudulent Transaction Detected!')
    else:
        st.success('Transaction is Safe.')