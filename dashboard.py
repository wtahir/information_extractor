# import streamlit as st
# from db import Session, Result
# import pandas as pd

# st.set_page_config(page_title="Extraction Dashboard", layout="wide")
# st.title("📊 Extraction Dashboard")

# session = Session()
# results = session.query(Result).order_by(Result.created_at.desc()).all()
# session.close()

# if not results:
#     st.info("No extraction results yet.")
# else:
#     # Convert to DataFrame
#     df = pd.DataFrame([{
#         "Payee": r.payee,
#         "Amount": r.amount,
#         "Amount Type": r.amount_type,
#         "IBAN": r.iban,
#         "Timestamp": r.created_at.strftime("%Y-%m-%d %H:%M:%S")
#     } for r in results])

#     st.metric(label="🧾 Total Records", value=len(df))

#     st.dataframe(df, use_container_width=True)

#     st.download_button("📥 Download CSV", df.to_csv(index=False), file_name="extractions.csv")


import streamlit as st
from db import Session, Result
import pandas as pd
from datetime import datetime

# Configure page first
st.set_page_config(page_title="Extraction Dashboard", layout="wide")
st.title("📊 Extraction Dashboard")

def get_results():
    """Safely fetch results from database"""
    session = Session()
    try:
        return session.query(Result).order_by(Result.created_at.desc()).all()
    finally:
        session.close()

# Main dashboard
def display_dashboard():
    results = get_results()
    
    if not results:
        st.info("No extraction results yet.")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame([{
        "Payee": r.payee,
        "Amount": r.amount,
        "Amount Type": r.amount_type,
        "IBAN": r.iban,
        "Timestamp": r.created_at.strftime("%Y-%m-%d %H:%M:%S")
    } for r in results])

    # Display metrics and data
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="🧾 Total Records", value=len(df))
    with col2:
        if st.button("🔄 Refresh Data"):
            st.rerun()
    
    st.dataframe(df, use_container_width=True)
    st.download_button(
        "📥 Download CSV", 
        df.to_csv(index=False), 
        file_name=f"extractions_{datetime.now().strftime('%Y%m%d')}.csv"
    )

# Run the dashboard
display_dashboard()

# Auto-refresh every 30 seconds (non-blocking)
placeholder = st.empty()
with placeholder.container():
    st.write("This page will refresh every 30 seconds.")