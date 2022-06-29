import joblib
import streamlit as st
import pandas as pd
from db_fxn import (create_table, add_data, view_all_data, get_note, view_unique_data, update_note_data, delete_note, get_category_notes, view_all_category, view_all_statuses, get_status_task_notes)
from db_users import (create_users_table, add_users_data, login_user, view_all_users)
import plotly.express  as px
import matplotlib.pyplot as plt
import seaborn as sns
import hashlib

import time
import requests
from datetime  import datetime, timedelta

special_chars = {'~', ':', "'", '+', '[', '\\', '@', '^', '{', '%', '(', '-', '"', '*', '|', ',', '&', '<', '`', '}', '.', '_', '=', ']', '!', '>', ';', '?', '#', '$', ')', '/'}

# Latest Weather App API and Functionality
weather_url = "https://api.openweathermap.org/data/2.5/weather?q={}&appid={}&units=imperial"
api_key = '72d6670e103c87bb241985ca33c7768a'

def getweather(city):
        result = requests.get(weather_url.format(city, api_key))
        if result:
                json = result.json()
                country = json['sys']['country']
                temp = json['main']['temp'] # Fahrenheit
                icon = json['weather'][0]['icon']
                des = json['weather'][0]['description']
                t_zone = json['timezone']
                res = [country, round(temp, 1), icon, des, t_zone]
                return res, json
        else:
                return st.warning('Error in location/weather!')

# identity verification
def generate_hashes(password):
        return hashlib.sha256(str.encode(password)).hexdigest()

def verify_hashes(password, hashed_text):
        if generate_hashes(password) == hashed_text:
                return hashed_text
        else:
                return False

def main():
        
        #hide_st_style = """
        #    <style>
        #    #MainMenu {visibility: hidden;}
        #    footer {visibility: hidden;}
        #    header {visibility: hidden;}
        #    </style>
        #    """
        # st.markdown(hide_st_style, unsafe_allow_html=True)
        
        #Title
        st.title("Notes ML App")
        
        # Logo
        st.markdown('''
                                <a href="javascript:document.getElementsByClassName('css-1ydp377 edgvbvh6')[1].click();">
                                        <img src="https://digisavvy.com/wp-content/uploads/2021/10/machine-learning-1.svg" alt="Logo ML" style="width:100px;height:100px;"/>
                                </a>
                                ''', unsafe_allow_html=True)

        # Menu
        menu = ['Home', 'Login', 'Sign Up', 'About']
        submenu = ["Add Note", "Read Notes and Reports", "Update Notes", "Delete Note"]
        
        choice = st.sidebar.selectbox("Menu", menu)

        if choice == 'Home':
                st.subheader("Home")
                st.write('This application auto-classifies your notes/tasks for you, and stores them in a local database. Functionality also exists to update and delete notes, view all notes or notes of a certain category, and see other reports. Please use the Sidebar on the left to login and begin using the application. Or, if this your first time, please sign up to use the application. Finally, you can learn more about the application from the Sidebar as well.')
        elif choice == 'Login':
                username = st.sidebar.text_input("Username")
                password = st.sidebar.text_input("Password", type = 'password')
                log_in = st.sidebar.checkbox('Login/Logout')
                
                if log_in:
                        create_users_table()
                        hashed_password = generate_hashes(password)
                        result = login_user(username, verify_hashes(password, hashed_password))
                        
                        # Initializing Session State
                        if 'current_user' not in st.session_state:
                                st.session_state['current_user'] = ''
                        
                        if 'current_city' not in st.session_state:
                                st.session_state['current_city'] = ''

                        if result:                                   
                                if username != st.session_state['current_user']: # first login
                                        st.session_state['current_user'] = username
                                        with st.empty():
                                                st.success('Welcome, {}!'.format(username))
                                placeholder = st.empty()

                                if st.session_state['current_city'] == '':
                                        
                                        with placeholder.container():
                                                city = st.text_input("Before we continue, what city are you currently in? (This is to show weather information throughout your session)")
                                        if len(city)>0:
                                                st.session_state['current_city'] = city
                                                res, json = getweather(city)
                                                web_str = "![Alt Text]"+"(https://openweathermap.org/img/wn/"+str(res[2])+"@2x.png)"
                                                placeholder.empty()
                                                st.info(str(round(res[1],1)) + " °F and " + res[3] + " in " + str(city) + web_str) # temp status city icon
                                                
                                               
                                        else:
                                                st.warning('Please enter a valid city')
                                                
                                else:
                                        city = st.session_state['current_city']
                                        res, json = getweather(city)
                                        web_str = "![Alt Text]"+"(https://openweathermap.org/img/wn/"+str(res[2])+"@2x.png)"
                                        st.info(str(round(res[1],1)) + " °F and " + res[3] + " in " + str(city) + web_str) # temp status city icon
                                
                                st.empty()

                                if st.session_state['current_city'] != "" and st.session_state['current_user'] == username:

                                        activity = st.selectbox('Please select from the activities below:', submenu)
                                        
                                        # Create database
                                        create_table()

                                        # Choice select

                                        if activity == 'Add Note':
                                                
                                                st.subheader('Add a New Note')

                                                # Layout
                                                col1, col2 = st.columns(2)
                                                with col1:
                                                        # Input text area
                                                        note = st.text_area("Enter your note:", height = 100)
                                                with col2:
                                                        # If note is a task
                                                        is_task = st.checkbox("Does this note contain a task or tasks?")
                                                        if is_task:
                                                                note_status = st.radio('Note Status', ['New', 'In Progress','On Hold', 'Complete'])
                                                                note_due_date = st.date_input('Due Date')
                                                        else:
                                                                note_status = ''
                                                                note_due_date = ''
                                                        
                                                # Categorize

                                                # Unpickle classifier
                                                clf = joblib.load("clf_final.pkl") # update with your own here

                                                # Get prediction
                                                pred_category = str(clf.predict([note])[0])
                                                
                                                # If button is pressed
                                                st.caption('NOTE: The highest predicted category will be used and stored by default. This can be edited by selecting Update Notes from above.')
                                                if st.button('Categorize Note'):
                                                        if note:
                                                                # Get latest prediction
                                                                pred_category = clf.predict([note])
                                                                pred_category = str(clf.predict([note])[0])

                                                                # Output prediction
                                                                st.write(f"This note can probably be categorized as: {pred_category}")
                                                                pred_prob = clf.predict_proba([note])
                                                                
                                                                # View all classes of model
                                                                st.write(clf.classes_)

                                                                # View probabilities of all classes for entered note
                                                                st.write(pred_prob)
                                                                pred_prob_df = pd.DataFrame(pred_prob, columns = ['Career', 'Education', 'Goals', 'Groceries', 'People', 'Religion', 'Travel'])

                                                                # Other Potential Categories (Conditional Display)

                                                                second_prob = 0
                                                                second_category = ''
                                                                for label, content in pred_prob_df.items():
                                                                        if (content[0] > second_prob) and (label != pred_category):
                                                                                second_prob = content[0]
                                                                                second_category = label

                                                                third_prob = 0
                                                                third_category = ''
                                                                for label, content in pred_prob_df.items():
                                                                        if (content[0] > third_prob) and (label != pred_category) and (label != second_category):
                                                                                third_prob = content[0]
                                                                                third_category = label

                                                                if second_prob > 0.25:
                                                                        if third_prob > 0.25:
                                                                                st.write(f'It can also be: {second_category}, or {third_category}')
                                                                        else:
                                                                                st.write(f'It can also be: {second_category}')
                                                                
                                                                st.caption("Prediction Probabilities by Category for Note")
                                                                st.dataframe(pred_prob_df)
                                                                st.bar_chart(pred_prob_df.iloc[0])

                                                                # st.snow()
                                                        
                                                        else:
                                                                st.warning('Please enter a note')

                                                if st.button("Add Note"):
                                                        if note:
                                                                add_data(username, note, is_task, note_status, note_due_date, pred_category) # Add data to database
                                                        
                                                                # Success message
                                                                st.success("Successfully added the new note: {}".format(note)) 
                                                                st.success("With a main predicted category of: {}".format(pred_category)) 

                                                        else:
                                                                st.warning('Please enter a note')
                                                
                                        elif activity == 'Read Notes and Reports':
                                                st.subheader('View All Notes and See Reports')
                                                result = view_all_data(username)
                                                # st.write(result)
                                                note_df = pd.DataFrame(result, columns = ['Note', 'Is Task?', 'Note Status', 'Note Due Date', 'Predicted Category'])
                                                with st.expander('View All Notes'):
                                                        st.dataframe(note_df)
                                                
                                                # Seeing notes of selected categories
                                                with st.expander('View All Notes of a Category'):
                                                        
                                                        # Fix this up (formatting)
                                                        current_categories = list(view_all_category(username)[i] for i in range(len(view_all_category(username))))
                                                        new_current_categories = []
                                                        for i in current_categories:
                                                                new_current_categories.append(i[0])

                                                        selected_category = st.selectbox('Choose a Category: ', new_current_categories)

                                                        selected_category_notes = get_category_notes(selected_category, username)

                                                        category_notes_df = pd.DataFrame(selected_category_notes, columns = ['Note', 'Is Task?', 'Note Status', 'Note Due Date', 'Predicted Category'])

                                                        st.dataframe(category_notes_df)
                                                
                                                # Report of Predicted Categories
                                                with st.expander('Report of All Notes by Predicted Category'):
                                                        p1 = px.pie(note_df, names = 'Predicted Category')
                                                        st.plotly_chart(p1)
                                                
                                                st.header("")

                                                # Seeing tasks of selected status
                                                with st.expander('View All Tasks of a Status'):
                                                        
                                                        # Fix this up (formatting)
                                                        current_statuses = list(view_all_statuses(username)[i] for i in range(len(view_all_statuses(username))))
                                                        new_current_statuses = []
                                                        for i in current_statuses:
                                                                new_current_statuses.append(i[0])

                                                        selected_status = st.selectbox('Choose a Status: ', new_current_statuses)

                                                        selected_status_task_notes = get_status_task_notes(selected_status, username)

                                                        status_task_df = pd.DataFrame(selected_status_task_notes, columns = ['Note', 'Is Task?', 'Note Status', 'Note Due Date', 'Predicted Category'])

                                                        st.dataframe(status_task_df)

                                                # Report of Tasks by Status
                                                with st.expander('Report of All Tasks by Status'):
                                                        task_df = note_df.loc[note_df['Is Task?'] == True]

                                                        p1 = px.pie(task_df, names = 'Note Status')
                                                        st.plotly_chart(p1)
                                                

                                        elif activity == 'Update Notes':
                                                st.subheader('Update All Notes')
                                                result = view_all_data(username)

                                                note_df = pd.DataFrame(result, columns = ['Note', 'Is Task?', 'Note Status', 'Note Due Date', 'Predicted Category'])
                                                with st.expander('Current Notes'):
                                                        st.dataframe(note_df)
                                                
                                                list_of_notes = [i[0] for i in view_unique_data(username)]

                                                selected_note = st.selectbox('Select a note to update: ', list_of_notes)

                                                selected_result = get_note(selected_note, username)

                                                # st.write(selected_result)

                                                if selected_result:
                                                        note = selected_result[0][0]
                                                        is_task = selected_result[0][1]
                                                        note_status = selected_result[0][2]
                                                        note_due_date = selected_result[0][3]
                                                        pred_category = selected_result[0][4]

                                                        # Layout
                                                        col1, col2 = st.columns(2)
                                                        with col1:
                                                                # Input text area
                                                                new_note = st.text_area("Enter your note:", note)
                                                        with col2:
                                                                # If note is a task
                                                                new_is_task = st.checkbox("Does this note contain a task or tasks?", is_task)
                                                        if new_is_task:
                                                                new_note_status = st.radio("Currently: " + str(note_status), ['New', 'In Progress','On Hold', 'Complete'])
                                                                new_note_due_date = st.date_input("Currently: " + str(note_due_date))
                                                        else:
                                                                new_note_status = ''
                                                                new_note_due_date = ''
                                                        
                                                # Unpickle classifier
                                                clf = joblib.load("clf_final.pkl")

                                                # Get prediction
                                                new_pred_category = str(clf.predict([new_note])[0])

                                                st.write(f"This note was previously categorized as: {pred_category}")
                                        
                                                pred_prob = clf.predict_proba([note])
                                                        
                                                # View all classes of model
                                                st.write(clf.classes_)

                                                # View probabilities of all classes for entered note
                                                st.write(pred_prob)
                                                pred_prob_df = pd.DataFrame(pred_prob, columns = ['Career', 'Education', 'Goals', 'Groceries', 'People', 'Religion', 'Travel'])



                                                # Other Potential Categories (Conditional Display)

                                                second_prob = 0
                                                second_category = ''
                                                for label, content in pred_prob_df.items():
                                                        if (content[0] > second_prob) and (label != pred_category):
                                                                second_prob = content[0]
                                                                second_category = label

                                                third_prob = 0
                                                third_category = ''
                                                for label, content in pred_prob_df.items():
                                                        if (content[0] > third_prob) and (label != pred_category) and (label != second_category):
                                                                third_prob = content[0]
                                                                third_category = label

                                                if second_prob > 0.25:
                                                        if third_prob > 0.25:
                                                                st.write(f'It also could have been: {second_category}, or {third_category}')
                                                        else:
                                                                st.write(f'It also could have been: {second_category}')
                                                
                                                st.caption("Prediction Probabilities by Category for Note (Past)")
                                                # st.dataframe(pred_prob_df)
                                                st.bar_chart(pred_prob_df.iloc[0])
                                                
                                                if st.button('Categorize Edited Note'):
                                                        # Get latest prediction
                                                        new_pred_category = str(clf.predict([new_note])[0])

                                                        # Output new prediction
                                                        
                                                        st.write(f"This note can now probably be categorized as: {new_pred_category}")

                                                        new_pred_prob = clf.predict_proba([new_note])
                                                        
                                                        # View all classes of model
                                                        st.write(clf.classes_)

                                                        # View probabilities of all classes for new entered note
                                                        st.write(new_pred_prob)
                                                        new_pred_prob_df = pd.DataFrame(new_pred_prob, columns = ['Career', 'Education', 'Goals', 'Groceries', 'People', 'Religion', 'Travel'])



                                                        # Other Potential Categories (Conditional Display)

                                                        new_second_prob = 0
                                                        new_second_category = ''
                                                        for label, content in new_pred_prob_df.items():
                                                                if (content[0] > new_second_prob) and (label != new_pred_category):
                                                                        new_second_prob = content[0]
                                                                        new_second_category = label

                                                        new_third_prob = 0
                                                        new_third_category = ''
                                                        for label, content in pred_prob_df.items():
                                                                if (content[0] > new_third_prob) and (label != new_pred_category) and (label != new_second_category):
                                                                        new_third_prob = content[0]
                                                                        new_third_category = label

                                                        if new_second_prob > 0.25:
                                                                if new_third_prob > 0.25:
                                                                        st.write(f'It can now also be: {new_second_category}, or {new_third_category}')
                                                                else:
                                                                        st.write(f'It can now also be: {new_second_category}')
                                                        
                                                        st.caption("New Prediction Probabilities by Category for Note")
                                                        st.dataframe(new_pred_prob_df)
                                                        st.bar_chart(new_pred_prob_df.iloc[0])

                                                st.caption("Note: If your answer to the below prompt is 'No', you will be given the option to manually enter a category. Otherwise, the new highest predicted category will be used.")
                                                manual_switch = st.radio("Are you okay with the note being edited to have the highest predicted category?", ['Yes', 'No'])
                                                if manual_switch == 'No':
                                                        new_pred_category = st.text_input('Manually enter a main category for the note being edited, then:', pred_category) 

                                                if st.button("Update Note"):

                                                        update_note_data(username, new_note, new_is_task, new_note_status, new_note_due_date, new_pred_category, note, is_task, note_status, note_due_date, pred_category) # Update note data in db
                                                
                                                        # Success message
                                                        st.success("Successfully updated the note to now be: \n{}".format(new_note)) 
                                                        st.success("With a predicted category now as: {}".format(new_pred_category))

                                                result2 = view_all_data(username)
                                                note_df2 = pd.DataFrame(result2, columns = ['Note', 'Is Task?', 'Note Status', 'Note Due Date', 'Predicted Category'])

                                                with st.expander('Updated Notes'):
                                                        st.dataframe(note_df2)

                                                        # All Tasks Complete Status Message :)
                                                        task_df = note_df2.loc[note_df2['Is Task?'] == True]
                                                        complete_task_df = task_df[task_df['Note Status'] == 'Complete']
                                                        if len(task_df) == len(complete_task_df):
                                                                st.balloons()
                                                                st.success('You finished all your task notes! Good work!')
                                        
                                        elif activity == 'Delete Note':
                                                st.subheader('Delete an Existing Note')
                                                
                                                result = view_all_data(username)
                                                note_df = pd.DataFrame(result, columns = ['Note', 'Is Task?', 'Note Status', 'Note Due Date', 'Predicted Category'])
                                                with st.expander('Current Notes'):
                                                        st.dataframe(note_df)

                                                list_of_notes = [i[0] for i in view_unique_data(username)]
                                                selected_note = st.selectbox('Select a note to delete: ', list_of_notes)
                                                st.warning('Are you sure you want to delete the note: "{}"?'.format(selected_note))
                                                if st.button('Delete Note'):
                                                        deleted_note = get_note(selected_note, username)
                                                        deleted_note = deleted_note[0][0] # extract only note
                                                        delete_note(selected_note, username)
                                                        st.success('The note "{}" has successfully been deleted'.format(deleted_note))
                                                
                                                result3 = view_all_data(username)
                                                note_df3 = pd.DataFrame(result3, columns = ['Note', 'Is Task?', 'Note Status', 'Note Due Date', 'Predicted Category'])

                                                with st.expander('Updated Notes'):
                                                        st.dataframe(note_df3)

                        else:
                                st.warning('Incorrect Username or Password... please retry')
                
                else: 
                        st.session_state.current_user = ""
                        st.session_state.current_city = ""
        
        elif choice == "Sign Up":
                new_username = st.text_input('Username')
                new_password = st.text_input("Password", type = 'password')
                if new_username:
                        if new_password:   
                                if len(new_password) >= 5: 
                                        l, u, p, d = 0, 0, 0, 0
                                        for i in new_password:
                                                # counting lowercase alphabets
                                                if (i.islower()):
                                                        l+=1           
                                        
                                                # counting uppercase alphabets
                                                if (i.isupper()):
                                                        u+=1           
                                        
                                                # counting digits
                                                if (i.isdigit()):
                                                        d+=1           
                                        
                                                # counting the mentioned special characters
                                                if(i in special_chars):
                                                        p+=1          
                                        if (l>=1 and u>=1 and p>=1 and d>=1 and l+p+u+d==len(new_password)):
                                                confirm_password = st.text_input('Confirm Password', type = 'password')
                                                if confirm_password: 
                                                        if new_password == confirm_password:
                                                                st.success('Passwords match!')
                                                                if st.button('Submit'):
                                                                        create_users_table()
                                                                        hashed_new_password = generate_hashes(new_password)
                                                                        add_users_data(new_username, hashed_new_password)
                                                                        st.success('You have successfully created a new account!')
                                                                        st.info('Login to get started with the Notes ML App from the Sidebar!')
                                                        else: 
                                                                st.warning('Passwords are not the same!')
                                                else:
                                                        st.warning('Please enter a confirm password')
                                        else:
                                                st.warning('Password must contain an uppercase, a lowercase, a digit, and a special character')
                                else:
                                        st.warning('Password must be at least 5 characters long')
                        else:
                                st.warning('Please enter a password')
                else:
                        st.warning('Please enter a username')
                st.caption('Note: username and password are case sensitive!')

        elif choice == 'About':
                st.write('')
                st.write('')
                st.image('https://i.imgur.com/sOTG2CF.jpg', caption = "Winter Park, Colorado (my wife's favorite picture of me)", width=300)
                st.subheader('About the Author/Application')
                st.write("This application was designed with <3 by Arifeen Saeed, who is currently a Deloitte Consulting Analyst in Austin, TX. Inspired by his own usage of the Google Keep and Apple Notes Apps, Arifeen was looking for a way to auto-classify his notes which easily get messy due to a quick jotting-down, and then the idea of using Streamlit dawned upon him. Combining SQL and Database Management, Python, Pandas, NumPy, and Machine Learning using scikit-learn and other libaries, this powerful data science application can serve as a repo for all your tasks and notes, and keep them sorted and timely. It can even output a report of the categories of your notes. Version 8 of includes more predictive prowess due to better training data, weather, more insights on your predictions, as well as UI changes. Additionally, data from Kaggle and elsewhere was utilized (sourced below). Users can also log-in and sign up now and have their notes securely stored for their own accounts, accessible on any device, any time, any where. Arifeen hopes this is one of the many projects that will lead him to a Master in Computer Science (MSCS), concentrating in Machine Learning, insha'Allah (God-willing).")
                st.text("")
                st.text('Datasets/sources used so far:')
                st.text('SimpleMaps World Cities Basic v 1.75')
                st.text('Grocery UPC Database')
                st.text('QURAN English')
                # st.text('Pokemon.csv (GitHub)')
                st.text('1000 Things I Want to Do in My Life (Choosing Figs website)')
                st.text('World University Rankings Kaggle')
                st.text('College Majors (Kaggle)')
                st.text('FiveThirtyEight Most Common Name Dataset (Kaggle)')
                st.text('Forbes Global Companies in 2022 (Kaggle)')
                st.text('Standard Occupational Classification (US Bureau of Labor Statistics)')
                st.text('GeoNames All Countries Points of Interests')
                st.text('Groceries Dataset Kaggle')
                st.text('Bible verses from King James Version Kaggle')
                st.text('New Years Resolutions Twitter Kaggle')
                st.text('10000 Things to Do Before You Die aussieontheroad')
                st.text('Google Answers Q: List of universities/colleges and their Abbreviations')
                st.text('Forebears Most Popular First Names in the World')
                st.text('SSA.gov most common names 1000')
                st.text('Brandedgirls.com Modern Names for Muslim Girls')
                st.text('Babynamemeaningz.com/3-islamic-boys-names')
                st.text('Fortune 1000 companies in 2021 and 2022 Kaggle')
                st.text('Exploring Monster.com Job Postings Kaggle')

                # Pokemon!
                st.write("")
                st.write("")
                st.write("")
                st.markdown('''
                                <a href="javascript:document.getElementsByClassName('css-1ydp377 edgvbvh6')[1].click();">
                                        <img src="https://64.media.tumblr.com/c15b061360fa577cfa6fa1868bc45962/tumblr_o2d65b8VYl1so9b4uo1_500.gifv" alt="Logo ML" style="width:100px;height:75px;"/>
                                </a>
                                ''', unsafe_allow_html=True)
                st.caption('Thanks for reading!')

if __name__ == '__main__':
        main()
