import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import altair as alt
import time
import zipfile
import pandas as pd
import datetime
import re

# Page title
st.set_page_config(page_title='Search Old Logs', page_icon='🤖')
st.title('🤖 ML Model Building')

with st.expander('About this app'):
  st.markdown('**What can this app do?**')
  st.info('This app allow users to build a machine learning (ML) model in an end-to-end workflow. Particularly, this encompasses data upload, data pre-processing, ML model building and post-model analysis.')

  st.markdown('**How to use the app?**')
  st.warning('To engage with the app, go to the sidebar and 1. Select a data set and 2. Adjust the model parameters by adjusting the various slider widgets. As a result, this would initiate the ML model building process, display the model results as well as allowing users to download the generated models and accompanying data.')

  st.markdown('**Under the hood**')
  st.markdown('Data sets:')
  st.code('''- Drug solubility data set
  ''', language='markdown')
  
  st.markdown('Libraries used:')
  st.code('''- Pandas for data wrangling
- Scikit-learn for building a machine learning model
- Altair for chart creation
- Streamlit for user interface
  ''', language='markdown')


# Sidebar for accepting input parameters
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
                    date_str =link.split('/')[-1].split('_')[-2]
                    if not is_valid_datestring(date_str):
                        can_continue = False
                        st.write(f"Check date format in Url, follow YYYYMMDD")


        # update dataframe state
        if can_continue:
            #check for datetime
            
            to_upload = {
                "question": input_question,
                "documents": input_values,
                "autoApprove": True
            }

            st.text(to_upload)




    

        
      
    # # Download example data
    # @st.cache_data
    # def convert_df(input_df):
    #     return input_df.to_csv(index=False).encode('utf-8')
    # example_csv = pd.read_csv('https://raw.githubusercontent.com/dataprofessor/data/master/delaney_solubility_with_descriptors.csv')
    # csv = convert_df(example_csv)
    # st.download_button(
    #     label="Download example CSV",
    #     data=csv,
    #     file_name='delaney_solubility_with_descriptors.csv',
    #     mime='text/csv',
    # )

    # # Select example data
    # st.markdown('**1.2. Use example data**')
    # example_data = st.toggle('Load example data')
    # if example_data:
    #     df = pd.read_csv('https://raw.githubusercontent.com/dataprofessor/data/master/delaney_solubility_with_descriptors.csv')

    # st.header('2. Set Parameters')
    # parameter_split_size = st.slider('Data split ratio (% for Training Set)', 10, 90, 80, 5)


    # st.subheader('2.1. Learning Parameters')
    # with st.expander('See parameters'):
    #     parameter_n_estimators = st.slider('Number of estimators (n_estimators)', 0, 1000, 100, 100)
    #     parameter_max_features = st.select_slider('Max features (max_features)', options=['all', 'sqrt', 'log2'])
    #     parameter_min_samples_split = st.slider('Minimum number of samples required to split an internal node (min_samples_split)', 2, 10, 2, 1)
    #     parameter_min_samples_leaf = st.slider('Minimum number of samples required to be at a leaf node (min_samples_leaf)', 1, 10, 2, 1)

    # st.subheader('2.2. General Parameters')
    # with st.expander('See parameters', expanded=False):
    #     parameter_random_state = st.slider('Seed number (random_state)', 0, 1000, 42, 1)
    #     parameter_criterion = st.select_slider('Performance measure (criterion)', options=['squared_error', 'absolute_error', 'friedman_mse'])
    #     parameter_bootstrap = st.select_slider('Bootstrap samples when building trees (bootstrap)', options=[True, False])
    #     parameter_oob_score = st.select_slider('Whether to use out-of-bag samples to estimate the R^2 on unseen data (oob_score)', options=[False, True])

    # sleep_time = st.slider('Sleep time', 0, 3, 0)

# Initiate the model building process
if uploaded_file or example_data: 
    with st.status("Running ...", expanded=True) as status:
    
        st.write("Loading data ...")
        time.sleep(sleep_time)

        st.write("Preparing data ...")
        time.sleep(sleep_time)
        X = df.iloc[:,:-1]
        y = df.iloc[:,-1]
            
        st.write("Splitting data ...")
        time.sleep(sleep_time)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=(100-parameter_split_size)/100, random_state=parameter_random_state)
    
        st.write("Model training ...")
        time.sleep(sleep_time)

        if parameter_max_features == 'all':
            parameter_max_features = None
            parameter_max_features_metric = X.shape[1]
        
        rf = RandomForestRegressor(
                n_estimators=parameter_n_estimators,
                max_features=parameter_max_features,
                min_samples_split=parameter_min_samples_split,
                min_samples_leaf=parameter_min_samples_leaf,
                random_state=parameter_random_state,
                criterion=parameter_criterion,
                bootstrap=parameter_bootstrap,
                oob_score=parameter_oob_score)
        rf.fit(X_train, y_train)
        
        st.write("Applying model to make predictions ...")
        time.sleep(sleep_time)
        y_train_pred = rf.predict(X_train)
        y_test_pred = rf.predict(X_test)
            
        st.write("Evaluating performance metrics ...")
        time.sleep(sleep_time)
        train_mse = mean_squared_error(y_train, y_train_pred)
        train_r2 = r2_score(y_train, y_train_pred)
        test_mse = mean_squared_error(y_test, y_test_pred)
        test_r2 = r2_score(y_test, y_test_pred)
        
        st.write("Displaying performance metrics ...")
        time.sleep(sleep_time)
        parameter_criterion_string = ' '.join([x.capitalize() for x in parameter_criterion.split('_')])
        #if 'Mse' in parameter_criterion_string:
        #    parameter_criterion_string = parameter_criterion_string.replace('Mse', 'MSE')
        rf_results = pd.DataFrame(['Random forest', train_mse, train_r2, test_mse, test_r2]).transpose()
        rf_results.columns = ['Method', f'Training {parameter_criterion_string}', 'Training R2', f'Test {parameter_criterion_string}', 'Test R2']
        # Convert objects to numerics
        for col in rf_results.columns:
            rf_results[col] = pd.to_numeric(rf_results[col], errors='ignore')
        # Round to 3 digits
        rf_results = rf_results.round(3)
        
    status.update(label="Status", state="complete", expanded=False)

    # Display data info
    st.header('Input data', divider='rainbow')
    col = st.columns(4)
    col[0].metric(label="No. of samples", value=X.shape[0], delta="")
    col[1].metric(label="No. of X variables", value=X.shape[1], delta="")
    col[2].metric(label="No. of Training samples", value=X_train.shape[0], delta="")
    col[3].metric(label="No. of Test samples", value=X_test.shape[0], delta="")
    
    with st.expander('Initial dataset', expanded=True):
        st.dataframe(df, height=210, use_container_width=True)
    with st.expander('Train split', expanded=False):
        train_col = st.columns((3,1))
        with train_col[0]:
            st.markdown('**X**')
            st.dataframe(X_train, height=210, hide_index=True, use_container_width=True)
        with train_col[1]:
            st.markdown('**y**')
            st.dataframe(y_train, height=210, hide_index=True, use_container_width=True)
    with st.expander('Test split', expanded=False):
        test_col = st.columns((3,1))
        with test_col[0]:
            st.markdown('**X**')
            st.dataframe(X_test, height=210, hide_index=True, use_container_width=True)
        with test_col[1]:
            st.markdown('**y**')
            st.dataframe(y_test, height=210, hide_index=True, use_container_width=True)

    # Zip dataset files
    df.to_csv('dataset.csv', index=False)
    X_train.to_csv('X_train.csv', index=False)
    y_train.to_csv('y_train.csv', index=False)
    X_test.to_csv('X_test.csv', index=False)
    y_test.to_csv('y_test.csv', index=False)
    
    list_files = ['dataset.csv', 'X_train.csv', 'y_train.csv', 'X_test.csv', 'y_test.csv']
    with zipfile.ZipFile('dataset.zip', 'w') as zipF:
        for file in list_files:
            zipF.write(file, compress_type=zipfile.ZIP_DEFLATED)

    with open('dataset.zip', 'rb') as datazip:
        btn = st.download_button(
                label='Download ZIP',
                data=datazip,
                file_name="dataset.zip",
                mime="application/octet-stream"
                )
    
    # Display model parameters
    st.header('Model parameters', divider='rainbow')
    parameters_col = st.columns(3)
    parameters_col[0].metric(label="Data split ratio (% for Training Set)", value=parameter_split_size, delta="")
    parameters_col[1].metric(label="Number of estimators (n_estimators)", value=parameter_n_estimators, delta="")
    parameters_col[2].metric(label="Max features (max_features)", value=parameter_max_features_metric, delta="")
    
    # Display feature importance plot
    importances = rf.feature_importances_
    feature_names = list(X.columns)
    forest_importances = pd.Series(importances, index=feature_names)
    df_importance = forest_importances.reset_index().rename(columns={'index': 'feature', 0: 'value'})
    
    bars = alt.Chart(df_importance).mark_bar(size=40).encode(
             x='value:Q',
             y=alt.Y('feature:N', sort='-x')
           ).properties(height=250)

    performance_col = st.columns((2, 0.2, 3))
    with performance_col[0]:
        st.header('Model performance', divider='rainbow')
        st.dataframe(rf_results.T.reset_index().rename(columns={'index': 'Parameter', 0: 'Value'}))
    with performance_col[2]:
        st.header('Feature importance', divider='rainbow')
        st.altair_chart(bars, theme='streamlit', use_container_width=True)

    # Prediction results
    st.header('Prediction results', divider='rainbow')
    s_y_train = pd.Series(y_train, name='actual').reset_index(drop=True)
    s_y_train_pred = pd.Series(y_train_pred, name='predicted').reset_index(drop=True)
    df_train = pd.DataFrame(data=[s_y_train, s_y_train_pred], index=None).T
    df_train['class'] = 'train'
        
    s_y_test = pd.Series(y_test, name='actual').reset_index(drop=True)
    s_y_test_pred = pd.Series(y_test_pred, name='predicted').reset_index(drop=True)
    df_test = pd.DataFrame(data=[s_y_test, s_y_test_pred], index=None).T
    df_test['class'] = 'test'
    
    df_prediction = pd.concat([df_train, df_test], axis=0)
    
    prediction_col = st.columns((2, 0.2, 3))
    
    # Display dataframe
    with prediction_col[0]:
        st.dataframe(df_prediction, height=320, use_container_width=True)

    # Display scatter plot of actual vs predicted values
    with prediction_col[2]:
        scatter = alt.Chart(df_prediction).mark_circle(size=60).encode(
                        x='actual',
                        y='predicted',
                        color='class'
                  )
        st.altair_chart(scatter, theme='streamlit', use_container_width=True)

    
# Ask for CSV upload if none is detected
else:
    st.warning('👈 Upload a CSV file or click *"Load example data"* to get started!')
