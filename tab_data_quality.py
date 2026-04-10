import streamlit as st
from data import load_data_quality_report, load_bias_flags


def render() -> None:
    st.subheader("Data Quality Report")
    quality_df = load_data_quality_report()
    st.dataframe(quality_df, use_container_width=True)

    st.subheader("Bias Flags")
    bias_df = load_bias_flags()
    st.dataframe(bias_df, use_container_width=True)
