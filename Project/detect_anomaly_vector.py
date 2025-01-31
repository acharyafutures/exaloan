'''
This file contains the logic for detecting loan anomalies using vectorized approach.
We do mask the data and detect anomalies only if the masking is true, else we skip the loan. Saving the cost.
'''

import pandas as pd
import streamlit as st


def detect_loan_anomalies_vectorized(df: pd.DataFrame):
    try:
        anomalies_dict = {loan_id: set() for loan_id in df["Loan ID"]}

        #Data validation anomalies
        mask_invalid_interest_rate = df["Interest rate"].lt(0) | df["Interest rate"].gt(100)
        mask_invalid_loan_term = df["Loan term"].le(0)
        mask_invalid_credit_score = ~df["Credit score"].isin(["A", "B", "C", "D"])
        mask_invalid_outstanding_principal = df["Loan status"].eq("repaid") & df["Outstanding principal"].gt(0)
        mask_invalid_loan_amount = df["Loan amount"].lt(0)

        for loan_id, row in df[mask_invalid_interest_rate].iterrows():
            anomalies_dict[row["Loan ID"]].add("Invalid interest rate")
        for loan_id, row in df[mask_invalid_loan_term].iterrows():
            anomalies_dict[row["Loan ID"]].add("Invalid loan term")
        for loan_id, row in df[mask_invalid_credit_score].iterrows():
            anomalies_dict[row["Loan ID"]].add("Invalid credit score")
        for loan_id, row in df[mask_invalid_outstanding_principal].iterrows():
            anomalies_dict[row["Loan ID"]].add("Invalid outstanding principal")
        for loan_id, row in df[mask_invalid_loan_amount].iterrows():
            anomalies_dict[row["Loan ID"]].add("Invalid loan amount")

        #Payment ability anomalies
        mask_business = df["Loan status"].eq("granted") & df["Borrower type"].eq("business")
        mask_business_anomaly = mask_business & (df["Monthly payment"].gt(df["Annual profit"].div(12)))
        mask_individual = df["Loan status"].eq("granted") & df["Borrower type"].eq("individual")
        mask_individual_anomaly = mask_individual & (df["Monthly payment"].gt(df["Family income"]))

        for loan_id, row in df[mask_business_anomaly].iterrows():
            anomalies_dict[row["Loan ID"]].add("Monthly payment is greater than annual profit")
        for loan_id, row in df[mask_individual_anomaly].iterrows():
            anomalies_dict[row["Loan ID"]].add("Monthly payment is greater than borrower income")

        #Repayment date anomalies
        df["Expected repayment date"] = pd.to_datetime(df["Expected repayment date"], errors='coerce')
        df["Repayment date"] = pd.to_datetime(df["Repayment date"], errors='coerce')
        df['date_diff'] = (df['Repayment date'] - df['Expected repayment date']).dt.days

        mask_late = df['date_diff'].gt(90)
        mask_early = df['date_diff'].lt(0)

        for loan_id, row in df[mask_late].iterrows():
            anomalies_dict[row["Loan ID"]].add("Repayment date is later than expected repayment date")
        for loan_id, row in df[mask_early].iterrows():
            anomalies_dict[row["Loan ID"]].add("Repayment date is earlier than expected repayment date")

        anomalies_dict = _detect_payment_history_anomalities_vectorized(anomalies_dict, df)

    except KeyError as e:
        print("KeyError in detect_loan_anomalies_vectorized", e)
        st.toast(f"KeyError: {e}", icon="❌")

    return anomalies_dict


def _detect_payment_history_anomalities_vectorized(anomalies_dict, loan) -> dict:
    '''Function that detects payment history anomalies using:
        1. `Days late`
        2. `payments history(state whether pending late or paid with delay)`
    '''
    #Detecting days late anomaly
    mask_late_days = loan["Days late"].gt(90)
    for loan_id, row in loan[mask_late_days].iterrows():
        anomalies_dict[row["Loan ID"]].add(
            f"Re-payment date anomaly as {row['Days late']} is greater than 90 days threshold"
        )

    for _, loan in loan.iterrows():
        loan_id = loan["Loan ID"]
        payments = loan["payments"]
        if isinstance(payments, str):
            try:
                payments = eval(payments)
                threshold = 0.5
                matching_count = sum(
                    payment['State'] in ['pending late', 'paid with delay'] for payment in payments
                )
                if matching_count/len(payments) > threshold:
                    anomalies_dict[loan_id].add("Payments history are not consistent")
            except Exception as e:
                print("Error in payment history parsing", e)
                anomalies_dict[loan_id].add(f"Payment history parsing error {e}")
    return anomalies_dict
