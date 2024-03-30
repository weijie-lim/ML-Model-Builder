import altair as alt
import datetime
import json
import pandas as pd
import numpy as np
import streamlit as st
import time
import re
import requests

from modules.constants import Constants
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

if "has_facts_to_show" not in st.session_state:
    st.session_state.has_facts_to_show = False

if "answers_to_question" not in st.session_state:
    st.session_state.answers_to_question = {}

if "date_keys" not in st.session_state:
    st.session_state.date_keys = []

if "date_keys" not in st.session_state:
    st.session_state.date_keys = []

if "submit_facts_is_disabled" not in st.session_state:
    st.session_state.submit_facts_is_disabled = False

if "submit_query_is_disabled" not in st.session_state:
    st.session_state.submit_query_is_disabled = False

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

    st.header('✍ Upload Document URL(s) and Submit your Question! ✍')
    st.markdown('**1. Input Your URL(s) to Doc(s)**')
    number_inputs = st.number_input('Number of URL(s):', step=1, min_value=1, disabled=st.session_state.submit_query_is_disabled)

    input_values = [st.text_input(f'Insert URL {i+1}:', '', key=f"text_input_{i}", disabled=st.session_state.submit_query_is_disabled)
    for i in range(number_inputs)]
    
    for link in input_values:
        if is_valid_url(link):
            date_str =link.split('/')[-1].split('_')[-2]
            if not is_valid_datestring(date_str):
                st.write(f"Check date format in Url, follow YYYYMMDD format")
    
    st.caption('*For URL(s), please submit in a raw .txt format at the end. No parsing of HTML will work in this app example.')
    st.caption('**HTML document query or parsing can be done in the future for further app improvement')
    
    st.markdown('**2. Input Your Question**') 
    input_question = st.text_input("Ask your question", disabled=st.session_state.submit_query_is_disabled)

    st.markdown('**3 Select Date of Logs to Read From**')
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
        "What is the duration?",
        min_value=st.session_state.least_recent,
        max_value=st.session_state.most_recent,
        # value=datetime(2020, 1, 1),
        format="YYYY/MM/DD")

    st.markdown('**4. Do you want to clear previous historical documents?**')
    if st.button("Clear Document Cache", type="secondary", 
                 disabled=st.session_state.submit_query_is_disabled):
        redis = Redis(
            url=UPSTASH_REDIS_URL, 
            token=UPSTASH_REDIS_TOKEN
            )
        redis.set(REDIS_KEY, "")
        

    final_doc_list_by_date = []
    st.markdown('**5. If no, submit query now!**')
    if st.button("Submit Query", type="primary", 
                 disabled=st.session_state.submit_query_is_disabled):
        if st.session_state["tabs"] != []:
            st.session_state["tabs"] = []
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
                            st.session_state["tabs"].append(url.split('/')[-1])
                            st.session_state.date_keys.append(f'{date_str[0:4]}-{date_str[4:6]}-{date_str[6:]}')


        # update dataframe state
        if can_continue:
            to_upload = {
                "question": input_question,
                "documents": final_doc_list_by_date,
                "autoApprove": True
            }

            st.text(to_upload)
            x = requests.post(POST_URL_SUBMIT_DOC_QNS, json = to_upload)
            if x.status_code == 200:
                st.write("Submission success!",x.status_code)
            else:
                st.write("Please submit again!",x.status_code)
            
            y = requests.get(GET_ANSWERS)
            if y.status_code != 200:
                st.write("Error in Getting Answers ", y.status_code)
            else:
                st.session_state.has_facts_to_show = True
                st.write("Just got our Answers!", y.status_code)
                st.write(y.text)
                st.session_state.answers_to_question = json.loads(y.text)
                st.session_state.submit_query_is_disabled = True
                st.experimental_rerun()

# QUESTION CONTAINER
container = st.container(border=True)
container.write("☃ Question Asked ☃")
container.write(input_question)

st.divider()
if not st.session_state.has_facts_to_show:
    st.write("⌛ Facts will be shown below on submit ⌛")
    container5 = st.container(border=False)
    container5.write("")
    container5.caption("...Awaiting Submission of Query...")
    container5.write("")
else:
    st.write("✌ Facts are shown below, please choose which are to be retained ✌")


# get old data from redis before adding in the new ones
redis = Redis(
    url=UPSTASH_REDIS_URL, 
    token=UPSTASH_REDIS_TOKEN
    )
old_data = redis.get(REDIS_KEY)
if old_data is None:
    old_data = ''

if "store_submitted_for_tab" not in st.session_state:
    st.session_state.store_submitted_for_tab = []

# Allow users to add to source of truth
if st.session_state.has_facts_to_show == True:
    tabs = st.tabs(st.session_state["tabs"])
    st.session_state.store_submitted_for_tab = [{'chosen':[], 'rejected':[]} 
                                                for i in range(len(tabs))]
    
    # get relevant facts using date_keys
    for i in range(len(tabs)):
        #Facts
        answers = st.session_state.answers_to_question['factsByDay'][st.session_state.date_keys[i]]
        ans1 = answers[0]
        ans2 = answers[1]
        ans3 = answers[2]

        if ans1.strip() == "":
            ans1="<empty>"
        if ans2.strip() == "":
            ans2="<empty>"
        if ans3.strip() == "":
            ans4="<empty>"

        if ans1 == ans2:
            ans2 = "Duplicate: "+ ans2
        if ans1 == ans3:
            ans3 = "Duplicate: "+ ans3
        if ans2 == ans3:
            ans3 = "Duplicate: "+ ans3

        if ans1 not in st.session_state.store_submitted_for_tab[i]['rejected']:
            st.session_state.store_submitted_for_tab[i]['rejected'].append(ans1)
        if ans2 not in st.session_state.store_submitted_for_tab[i]['rejected']:
            st.session_state.store_submitted_for_tab[i]['rejected'].append(ans2)
        if ans3 not in st.session_state.store_submitted_for_tab[i]['rejected']:
            st.session_state.store_submitted_for_tab[i]['rejected'].append(ans3)


        with tabs[i]:


            st.write('Select correct answers:')
            option_1 = st.checkbox(label=f'{ans1}', 
                                key=f'opt1_{i}')
            
            option_2 = st.checkbox(label=f'{ans2}', 
                                key=f'opt2_{i}')
            
            option_3 = st.checkbox(label=f'{ans3}', 
                                key=f'opt3_{i}')

            if option_1:
                if ans1 not in st.session_state.store_submitted_for_tab[i]['chosen']:
                    st.session_state.store_submitted_for_tab[i]['chosen'].append(ans1)
                
                if ans1 in st.session_state.store_submitted_for_tab[i]['rejected']:
                    st.session_state.store_submitted_for_tab[i]['rejected'].remove(ans1)
            else:
                if ans1 in st.session_state.store_submitted_for_tab[i]['chosen']:
                    st.session_state.store_submitted_for_tab[i]['chosen'].remove(ans1)
                
                if ans1 not in st.session_state.store_submitted_for_tab[i]['rejected']:
                    st.session_state.store_submitted_for_tab[i]['rejected'].append(ans1)
                
            if option_2:
                if ans2 not in st.session_state.store_submitted_for_tab[i]['chosen']:
                    st.session_state.store_submitted_for_tab[i]['chosen'].append(ans2)
                
                if ans2 in st.session_state.store_submitted_for_tab[i]['rejected']:
                    st.session_state.store_submitted_for_tab[i]['rejected'].remove(ans2)
            else:
                if ans2 in st.session_state.store_submitted_for_tab[i]['chosen']:
                    st.session_state.store_submitted_for_tab[i]['chosen'].remove(ans2)

                if ans2 not in st.session_state.store_submitted_for_tab[i]['rejected']:
                    st.session_state.store_submitted_for_tab[i]['rejected'].append(ans2)
            
            if option_3:
                if ans3 not in st.session_state.store_submitted_for_tab[i]['chosen']:
                    st.session_state.store_submitted_for_tab[i]['chosen'].append(ans3)

                if ans3 in st.session_state.store_submitted_for_tab[i]['rejected']:
                    st.session_state.store_submitted_for_tab[i]['rejected'].remove(ans3)
            else:
                if ans3 in st.session_state.store_submitted_for_tab[i]['chosen']:
                    st.session_state.store_submitted_for_tab[i]['chosen'].remove(ans3)

                if ans3 not in st.session_state.store_submitted_for_tab[i]['rejected']:
                    st.session_state.store_submitted_for_tab[i]['rejected'].append(ans3)

if st.session_state.has_facts_to_show:
    submit_tab_options = st.button("Submit Checked Facts", 
                                type="primary", 
                                key=f'fact_sub_btn',
                                disabled=st.session_state.submit_facts_is_disabled
                                )
    if submit_tab_options:
        st.session_state.submit_facts_is_disabled = True
        for choices in st.session_state.store_submitted_for_tab:
            for j in choices['chosen']:
                old_data = old_data + '\n' + j
        
        # answers = st.session_state.answers_to_question['factsByDay'][st.session_state.date_keys[i]]
        
        data = redis.set(REDIS_KEY, old_data)
        
        if data:
            st.write("updated to redis as source of truth")
            st.session_state.has_facts_to_show = False
        else:
            st.write("Failed to write to redis as source of truth")
        st.experimental_rerun()

if st.session_state.submit_facts_is_disabled:
    for d in range(len(st.session_state.date_keys)):
        st.write(f'For date {st.session_state.date_keys[d]}')
        container2 = st.container(border=True)
        container2.write("Chosen Facts:")
        for theChosenOne in st.session_state.store_submitted_for_tab[d]['chosen']:
            container2.write(f'✔✔✔ {theChosenOne}')

        container3 = st.container(border=True)
        container3.write("Rejected Facts:")
        for theRejectedOne in st.session_state.store_submitted_for_tab[d]['rejected']:
            container3.write(f'✘✘✘ {theRejectedOne}')                

    reset_all_button = st.button(label="Reset to Submit New Data", 
                                    type="primary", 
                                    key=f'reset_all_tabs'
                                    )
    if reset_all_button:
        st.session_state.answers_to_question = {}
        st.session_state.store_submitted_for_tab.clear()
        st.session_state.date_keys.clear()
        st.session_state.has_facts_to_show = False
        st.session_state["tabs"].clear()
        st.session_state.submit_facts_is_disabled = False
        st.session_state.submit_query_is_disabled = False
        st.experimental_rerun()

st.divider()
st.title('🍾 Raw Data Structures 🍾')
st.write('answers_to_question', st.session_state.answers_to_question)
st.write('store_submitted_for_tab', st.session_state.store_submitted_for_tab)
st.write('date_keys', st.session_state.date_keys)
st.write('tabs', st.session_state["tabs"])
st.write('has_facts_to_show', st.session_state.has_facts_to_show)
st.write('submit_facts_is_disabled', st.session_state.submit_facts_is_disabled)