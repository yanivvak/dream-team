import streamlit as st    
import warnings  
  
warnings.filterwarnings('ignore')  

st.title("Autogen showcase")
st.write("This takes three easy steps!")


st.page_link( "pages/01_setup.py", icon="🤖", label="Step1: First, let's create a new agents.")

st.page_link( "pages/01_setup_transitions.py", icon="🔄", label="Step 2: Then, let's create a allowed transitions between agents.")

st.page_link("pages/02_run.py", icon="🏃‍♂️", label="Step 3: Then you can run you agent workflow.")