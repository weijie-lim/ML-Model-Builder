import altair as alt
import datetime
import pandas as pd
import numpy as np
import streamlit as st
import time
import re
import requests

from constants import Constants
from upstash_redis import Redis


POST_URL_SUBMIT_DOC_QNS = Constants.POST_URL_SUBMIT_DOC_QNS
GET_ANSWERS = Constants.GET_ANSWERS
UPSTASH_REDIS_URL = Constants.UPSTASH_REDIS_URL
UPSTASH_REDIS_TOKEN=Constants.UPSTASH_REDIS_TOKEN
UPSTASH_REDIS_PASSWORD=Constants.UPSTASH_REDIS_PASSWORD
REDIS_KEY=Constants.REDIS_KEY


# PAGE TITLE
st.set_page_config(page_title='Search Old Logs', page_icon='🤖')
st.title('🤖 Your Trusty AMA Bot 🤖')
input_question = ""

if "tabs" not in st.session_state:
    st.session_state["tabs"] = []

has_facts_to_show = False


# SIDEBAR FOR ACCEPTING INPUTS
with st.sidebar:

    def is_valid_url(url):
        url_regex = re.compile(r'https?://(?:www\.)?[a-zA-Z0-9./]+')
        return bool(url_regex.match(url))

    def is_valid_datestring(date_text):
        try:
            datetime.date.fromisoformat(date_text)
        except ValueError:
            return False
        return True

    st.header('Upload and Submit your Questions!')
    st.markdown('**1a. Input the URL of Log Files**')
    number_inputs = st.number_input('number of URLs', step=1, min_value=1)
    st.write('number of URLs to upload ', number_inputs)

    input_values = [st.text_input(f'URL No. {i+1}', '', key=f"text_input_{i}")
    for i in range(number_inputs)]
    
    for link in input_values:
        if is_valid_url(link):
            date_str =link.split('/')[-1].split('_')[-2]
            if not is_valid_datestring(date_str):
                st.write(f"Check date format in Url, follow YYYYMMDD format")
    
    st.markdown('**1b. Input Your Question**')  
    input_question = st.text_input("Ask your question")

    st.markdown('**1c. Select Date of Logs to Read From**')
    list_of_dates = []
    date_format = '%Y%m%d'
    now = datetime.datetime.now()
    if "least_recent" not in st.session_state:
        st.session_state.least_recent =now
    if "most_recent" not in st.session_state:
        st.session_state.most_recent = None

    for link in input_values:
        if is_valid_url(link):
            date_str =link.split('/')[-1].split('_')[-2]
            if is_valid_datestring(date_str):
                date_obj = datetime.datetime.strptime(date_str, date_format)
                list_of_dates.append(date_obj)
                if date_obj < st.session_state.least_recent:
                    st.session_state.least_recent = date_obj
                      
    if len(list_of_dates) > 1:
        if st.session_state.most_recent is None:
            st.session_state.most_recent = datetime.datetime(1900,1,1)

        for i, d in enumerate(list_of_dates):
            if d > st.session_state.most_recent:
                st.session_state.most_recent = d

    end_time = st.slider(
        "When do you start?",
        min_value=st.session_state.least_recent,
        max_value=st.session_state.most_recent,
        # value=datetime(2020, 1, 1),
        format="YYYY/MM/DD")

    final_doc_list_by_date = []
    if st.button("Submit", type="primary"):
        can_continue = True
        if input_question == None:
            st.write("Please enter your question!!!")
            can_continue = False
        elif len(input_question) < 10:
            st.write("Question is too short!!!")
            can_continue = False
        else:
            #check if all URLs are okay
            for i, url in enumerate(input_values):
                if not is_valid_url(url):
                    st.write(f"URL No. {i+1} is invalid!!!\r...")
                    can_continue = False
                else:
                    date_str =url.split('/')[-1].split('_')[-2]
                    if not is_valid_datestring(date_str):
                        can_continue = False
                        st.write(f"Check date format in Url, follow YYYYMMDD")
                    else:
                        #check for datetime
                        date_obj = datetime.datetime.strptime(date_str, date_format)
                        if date_obj.date() <= end_time.date():
                            final_doc_list_by_date.append(url)
                            st.session_state["tabs"].append(date_str)


        # update dataframe state
        if can_continue:

            to_upload = {
                "question": input_question,
                "documents": final_doc_list_by_date,
                "autoApprove": True
            }

            st.text(to_upload)
            x = requests.post(POST_URL_SUBMIT_DOC_QNS, json = to_upload)
            if x.status_code != 200:
                st.write("status code:",x.status_code)
            else:
                st.write("status code:",x.status_code)

# QUESTION CONTAINER
container = st.container(border=True)
container.write("Questions Asked:")
container.write(input_question)

st.write("Facts will be shown below on submit:")

# x = requests.get('https://w3schools.com')
# print(x.status_code)

submit_tab_options = st.button("Reset", type="secondary", disabled=False)

def disable(index):
    st.session_state.clicked[index] = True

# get old data from redis before adding in the new ones
redis = Redis(
    url=UPSTASH_REDIS_URL, 
    token=UPSTASH_REDIS_TOKEN
    )
old_data = redis.get(REDIS_KEY)
if old_data is None:
    old_data = ''

# Allow users to add to source of truth
if has_facts_to_show == True:
    tabs = st.tabs(st.session_state["tabs"])
    if 'clicked' not in st.session_state:
        st.session_state.clicked = [False for i in range(len(tabs))]
    else:
        st.session_state.clicked = [False for i in range(len(tabs))]
    for i in range(len(tabs)):
        with tabs[i]:
            tabs[i].write("this is tab 1")
            st.write('Select three known variables:')
            option_1 = st.checkbox('initial velocity (u)', 
                                   disabled=st.session_state.clicked[i])
            option_2 = st.checkbox('final velocity (v)', 
                                   disabled=st.session_state.clicked[i])
            option_3 = st.checkbox('acceleration (a)', 
                                   disabled=st.session_state.clicked[i])
            submit_tab_options = st.button("Reset", 
                                           type="secondary", 
                                           on_click=disable, 
                                           disabled=st.session_state.clicked[i])
            if submit_tab_options:
                if option_1: #is selected, submit to 
                    #new string
                    #new_data_str = old_data + "\n" + new_data_str
                    #data = redis.set(REDIS_KEY, new_data_str)
                    pass
                if option_2: #is selected
                    #new string
                    #new_data_str = old_data + "\n" + new_data_str
                    #data = redis.set(REDIS_KEY, new_data_str)
                    pass
                if option_3: #is selected
                    #new string
                    #new_data_str = old_data + "\n" + new_data_str
                    #data = redis.set(REDIS_KEY, new_data_str)
                    pass
    

    