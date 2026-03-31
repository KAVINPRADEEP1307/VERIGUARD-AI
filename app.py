import streamlit as st
import pandas as pd
import random
import time
import math
import requests
import sqlite3
from sklearn.tree import DecisionTreeClassifier

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="VeriGuard AI 🚨", layout="centered")

# ------------------ UI ------------------
st.markdown("""
<style>
.stApp {background-color: #0E1117; color: white;}
.block-container {max-width: 400px; margin: auto;}
.stButton>button {
    width: 100%;
    border-radius: 10px;
    background-color: #00FFCC;
    color: black;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.title("🚨 veriguard AI")
