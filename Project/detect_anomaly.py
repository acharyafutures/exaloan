'''
This file contains the logic for detecting loan anomalies using naive approach.
We do iterate through each loan and detect anomalies based on the given conditions.
'''

import pandas as pd
import streamlit as st



def detect_loan_anomalies(df: pd.DataFrame):
    anomalies_dict = {}
    try:
        for _, loan in df.iterrows():
            loan_id = loan["Loan ID"]
            anomalies_dict[loan_id] = set()

            # Data validation anomalities
            anomalies_dict = _data_validation_anomalies(anomalies_dict, loan)
            
            # Detecting repayment date anomaly
            anomalies_dict = _detect_payment_history_anomalities_normal(anomalies_dict, loan)

            #Checking if expected repayment date was earlier than actual repayment date
            anomalies_dict = _detect_repayment_anomalities(anomalies_dict, loan)

            anomalies_dict = _detect_payment_ability_anomalities(anomalies_dict, loan)

    except KeyError as e:
        print("KeyError in detect_loan_anomalies", e)
        st.toast(f"KeyError: {e}", icon="❌")

    return anomalies_dict


def _detect_payment_ability_anomalities(anomalies_dict, loan) -> dict:
    '''
        Function that detects payment ability anomalies based on:
            `Monthly Payment` and `annual profit` if `borrower type` is business and
            `Monthly Payment` and `borrower income` if `borrower type` is individual
    '''
    loan_id = loan["Loan ID"]
    loan_status = loan["Loan status"]
    monthly_payment = loan["Monthly payment"]
    annual_profit = loan["Annual profit"]
    borrower_type = loan["Borrower type"]
    family_income = loan["Family income"]

    if loan_status == "granted":
        if borrower_type == "business":
            if monthly_payment > (annual_profit/12):
                anomalies_dict[loan_id].add("Monthly payment is greater than annual profit")
        if borrower_type == "individual":
            if monthly_payment > family_income:
                anomalies_dict[loan_id].add("Monthly payment is greater than borrower income")

    return anomalies_dict


def _detect_repayment_anomalities(anomalies_dict, loan) -> dict:
    '''
        Function that detects repayment date anomalies as earlier than expected repayment date
        leads to getting less interest, and if later than expected repayment date
        leads to less profit or even no profit
    '''
    loan_id = loan["Loan ID"]
    expected_date = pd.to_datetime(loan['Expected repayment date'], errors='coerce')
    repayment_date = pd.to_datetime(loan['Repayment date'], errors='coerce')    
    if pd.notna(expected_date) and pd.notna(repayment_date):
        date_dif = repayment_date-expected_date
        if date_dif.days > 90:
            anomalies_dict[loan_id].add(
                    f"Repayment date is later than expected repayment date by {date_dif.days} days"
                )
        if date_dif.days < 0:
            anomalies_dict[loan_id].add(
                    f"Repayment date is earlier than expected repayment date by {abs(date_dif.days)} days"
                )
    return anomalies_dict


def _detect_payment_history_anomalities_normal(anomalies_dict, loan) -> dict:
    '''Function that detects payment history anomalies using:
        1. `Days late`
        2. `payments history(state whether pending late or paid with delay)`
    '''
    loan_id = loan["Loan ID"]

    days_late = loan["Days late"]
    if days_late > 90:
            anomalies_dict[loan_id].add(
                    f"Re-payment date anomaly as {days_late} is greater than 90 days threshold"
                )
    
    #Detecting payments history anomaly
    payments = loan["payments"]
    if isinstance(payments, str):
        try:
            payments = eval(payments)
                #Checking if most of the payments state are pending late or paid with delay
            threshold = 0.5
            matching_count = sum(
                payment['State'] in ['pending late', 'paid with delay'] for payment in payments
            )
            if matching_count/len(payments) > threshold:
                anomalies_dict[loan_id].add(f"Payments history are not consistent")
                
        except Exception as e:
            print("Error in payment history parsing", e)
            anomalies_dict[loan_id].add(f"Payment history parsing error {e}")
    
    return anomalies_dict

def _data_validation_anomalies(anomalies_dict, loan) -> dict:
    '''Function that checks for data validation'''
    loan_id = loan["Loan ID"]

    if loan["Interest rate"] < 0 or loan["Interest rate"] > 100:
        anomalies_dict[loan_id].add("Invalid interest rate")
    if loan["Loan term"] <= 0:
        anomalies_dict[loan_id].add("Loan term must be positive non-zero value")
    if loan["Credit score"] not in ["A", "B", "C", "D"]:
        anomalies_dict[loan_id].add("Credit score not in range")
    if loan["Loan status"] == "repaid" and loan["Outstanding principal"] > 0:
        anomalies_dict[loan_id].add("Outstanding principal must be 0 when loan status is repaid")
    if loan["Loan amount"] < 0:
        anomalies_dict[loan_id].add("Loan amount must be positive")
    
    return anomalies_dict
