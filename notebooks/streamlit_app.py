# streamlit_app.py

import streamlit as st
from rag_pipeline import get_answer

st.title("Deutsche Hochschule für Studien Academic Advisor Chatbot")

user_query = st.text_input("Ask your question:")

if st.button("Submit"):
    if user_query:
        answer = get_answer(user_query)
        st.markdown("**Answer:**")
        st.write(answer)

st.caption("Developed by Ifeoma Adigwe • Powered by Streamlit")
