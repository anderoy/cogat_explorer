import streamlit as st
# To make things easier later, we're also importing numpy and pandas for
# working with sample data.
import numpy as np
import pandas as pd
import altair as alt

st.set_page_config(  # Alternate names: setup_page, page, layout
	layout="wide",  # Can be "centered" or "wide". In the future also "dashboard", etc.
	initial_sidebar_state="expanded",  # Can be "auto", "expanded", "collapsed"
	page_title='CogAT Score Explorer',  # String or None. Strings get appended with "• Streamlit". 
	page_icon=None,  # String, anything supported by st.image, or None.
)

############ Data Import
cogat = pd.read_csv('trimmed.csv')
cogat['Composite Grade Percentile'] = np.where(cogat['Class Grade'] < 3,
                                               cogat['Grade Percentile Rank (GPR) VQ'],
                                               cogat['Grade Percentile Rank (GPR) VQN'])
cogat['Decision'] = 'Decline'
cogat['School ID'] = np.where(cogat['top-choice school'] == 'Bates Academy', 2882,
                     np.where(cogat['top-choice school'] == 'Foreign Language Immersion and Cultural Studies School', 7326,
                     np.where(cogat['top-choice school'] == 'Chrysler Elementary (Grades K-5)', 689,
                     np.where(cogat['top-choice school'] == 'Paul Robeson/Malcolm X Academy', 7633,
                     np.where(cogat['top-choice school'] == 'Golightly Education Center', 176, 0)))))


############# Layout Area 
st.sidebar.title('CogAt Score Explorer')

overview = st.beta_container()

stanine = st.beta_container()

stanine1, stanine2, stanine3 = st.beta_columns(3)

outputs = st.beta_container()


############# Sidebar Toggles

if st.sidebar.checkbox('Show Overview', value=True):
  with overview:
    st.subheader('Overview')
    # Add info about how the groupings arew calculated from the test company
    # Note that these are "National Percentiles"
    'All comparison scores that we look at (Percentiles, Stanine, Scale Scores, etc.) are compared to the National results from all students who completed the CogAT during the same testing window.'
    'The Stanine Performance Groups can help us get a quick understanding of how our applicants fared in comparison to all other test takers. The graphic below (and on the lower left) provides a quick overview of the Stanine groups and their percentile ranges.'
    st.image('stanine.png')
    'Since many applicants entering Kindergarten did not meet the lower age limit for age-based comparisons, we will have to rely on grade-level comparison scores. We just have to keep in mind that applicants were essentially testing "up" a grade level.'
    st.write('The table below shows the total number of applications per top-choice school by grade')
    app_count = pd.pivot_table(cogat, index='Class Grade', columns='top-choice school', aggfunc='size', fill_value=0)
    app_count

option = st.sidebar.selectbox(
  'What grade level would you like to view?',
  cogat['Class Grade'].unique())

grade = cogat.loc[cogat['Class Grade'] == option]

b_cut = st.sidebar.slider('Set lowest accepted value for Bates acceptance', min_value=1, max_value=75, step=1, value=23)
b_wcut = st.sidebar.slider('Set lowest accepted value for Bates School Review', min_value=1, max_value=75, step=1, value=11)
cut = st.sidebar.slider('Set lowest accepted value for acceptance', min_value=1, max_value=75, step=1, value=11)
wcut = st.sidebar.slider('Set lowest accepted value for School Review', min_value=1, max_value=75, step=1, value=4)


############# Calculations

grade.loc[(grade['Composite Grade Percentile'] >= b_wcut) & (grade['top-choice school'] == 'Bates Academy'), 'Decision'] = 'School Review'
grade.loc[(grade['Composite Grade Percentile'] >= b_cut) & (grade['top-choice school'] == 'Bates Academy'), 'Decision'] = 'Accept'
grade.loc[(grade['Composite Grade Percentile'] >= wcut) & (grade['top-choice school'] != 'Bates Academy'), 'Decision'] = 'School Review'
grade.loc[(grade['Composite Grade Percentile'] >= cut) & (grade['top-choice school'] != 'Bates Academy'), 'Decision'] = 'Accept'

results = pd.pivot_table(grade, columns='Decision', index=['School ID', 'top-choice school'], aggfunc='size', fill_value=0)
results.reset_index(inplace=True)
results = results.rename(columns = {'top-choice school': 'School'})
capacity = pd.read_csv('capacity.csv')
results = pd.merge(results, capacity[['School ID', str(option)]], on='School ID', how='left')
results = results.rename(columns= {str(option): 'Capacity'})

if st.sidebar.checkbox('Show Placement Results'):
  with outputs:
    st.title('Placement results based on cut scores')
    results

if st.sidebar.checkbox('Show Stanine Performance Groups'):
  with stanine:
    st.subheader('Currently viewing a total of ' + str(grade.shape[0]) + ' applicants')
    st.title('Composite Grouping')
    if option < 3:
      st.subheader(str('Grade Stanine (GS) VQ') + ' Performance Group')
      hist_values = grade['Grade Stanine (GS) VQ'].value_counts().to_frame()
      hist_values.columns = ['Count']
      for i in [1,2,3,4,5,6,7,8,9]:
        if i in hist_values.index:
          continue
        else:
          hist_values.loc[i] = [0]
      hist_values.reset_index(inplace=True)
      hist_values = hist_values.rename(columns = {'index':'Performance Group'})
      hist_values['Performance Group'] = hist_values['Performance Group'].astype('Int64').astype(str)
      test = alt.Chart(hist_values).mark_bar().encode(
        x='Performance Group',
        y='Count',
        tooltip=['Count']
      )
      st.altair_chart(test, use_container_width=True)
    else:
      st.subheader(str('Grade Stanine (GS) VQN') + ' Performance Group')
      hist_values = grade['Grade Stanine (GS) VQN'].value_counts().to_frame()
      hist_values.columns = ['Count']
      for i in [1,2,3,4,5,6,7,8,9]:
        if i in hist_values.index:
          continue
        else:
          hist_values.loc[i] = [0]
      hist_values.reset_index(inplace=True)
      hist_values = hist_values.rename(columns = {'index':'Performance Group'})
      hist_values['Performance Group'] = hist_values['Performance Group'].astype('Int64').astype(str)
      test = alt.Chart(hist_values).mark_bar().encode(
        x='Performance Group',
        y='Count',
        tooltip=['Count']
      )
      st.altair_chart(test, use_container_width=True)


  with stanine1:
    st.title('Verbal')
    st.subheader(str('Grade Stanine (GS) V') + ' Performance Group')
    hist_values = grade['Grade Stanine (GS) V'].value_counts().to_frame()
    hist_values.columns = ['Count']
    for i in [1,2,3,4,5,6,7,8,9]:
      if i in hist_values.index:
        continue
      else:
        hist_values.loc[i] = [0]
    hist_values.reset_index(inplace=True)
    hist_values = hist_values.rename(columns = {'index':'Performance Group'})
    hist_values['Performance Group'] = hist_values['Performance Group'].astype('Int64').astype(str)
    test = alt.Chart(hist_values).mark_bar().encode(
      x='Performance Group',
      y='Count',
      tooltip=['Count']
    )
    st.altair_chart(test, use_container_width=True)

  with stanine2:
    st.title('Quantitative')
    st.subheader(str('Grade Stanine (GS) Q') + ' Performance Group')
    hist_values = grade['Grade Stanine (GS) Q'].value_counts().to_frame()
    hist_values.columns = ['Count']
    for i in [1,2,3,4,5,6,7,8,9]:
      if i in hist_values.index:
        continue
      else:
        hist_values.loc[i] = [0]
    hist_values.reset_index(inplace=True)
    hist_values = hist_values.rename(columns = {'index':'Performance Group'})
    hist_values['Performance Group'] = hist_values['Performance Group'].astype('Int64').astype(str)
    test = alt.Chart(hist_values).mark_bar().encode(
      x='Performance Group',
      y='Count',
      tooltip=['Count']
    )
    st.altair_chart(test, use_container_width=True)

  with stanine3:
    st.title('Non-verbal')
    st.subheader(str('Grade Stanine (GS) N') + ' Performance Group')
    hist_values = grade['Grade Stanine (GS) N'].value_counts().to_frame()
    hist_values.columns = ['Count']
    for i in [1,2,3,4,5,6,7,8,9]:
      if i in hist_values.index:
        continue
      else:
        hist_values.loc[i] = [0]
    hist_values.reset_index(inplace=True)
    hist_values = hist_values.rename(columns = {'index':'Performance Group'})
    hist_values['Performance Group'] = hist_values['Performance Group'].astype('Int64').astype(str)
    test = alt.Chart(hist_values).mark_bar().encode(
      x='Performance Group',
      y='Count',
      tooltip=['Count']
    )
    st.altair_chart(test, use_container_width=True)

  with stanine1:
    st.subheader(str('Age Stanine (AS) V') + ' Performance Group')
    hist_values = grade['Age Stanine (AS) V'].value_counts().to_frame()
    hist_values.columns = ['Count']
    for i in [1,2,3,4,5,6,7,8,9]:
      if i in hist_values.index:
        continue
      else:
        hist_values.loc[i] = [0]
    hist_values.reset_index(inplace=True)
    hist_values = hist_values.rename(columns = {'index':'Performance Group'})
    hist_values['Performance Group'] = hist_values['Performance Group'].astype('Int64').astype(str)
    test = alt.Chart(hist_values).mark_bar().encode(
      x='Performance Group',
      y='Count',
      tooltip=['Count']
    )
    st.altair_chart(test, use_container_width=True)

  with stanine2:
    st.subheader(str('Age Stanine (AS) Q') + ' Performance Group')
    hist_values = grade['Age Stanine (AS) Q'].value_counts().to_frame()
    hist_values.columns = ['Count']
    for i in [1,2,3,4,5,6,7,8,9]:
      if i in hist_values.index:
        continue
      else:
        hist_values.loc[i] = [0]
    hist_values.reset_index(inplace=True)
    hist_values = hist_values.rename(columns = {'index':'Performance Group'})
    hist_values['Performance Group'] = hist_values['Performance Group'].astype('Int64').astype(str)
    test = alt.Chart(hist_values).mark_bar().encode(
      x='Performance Group',
      y='Count',
      tooltip=['Count']
    )
    st.altair_chart(test, use_container_width=True)

  with stanine3:
    st.subheader(str('Age Stanine (AS) N') + ' Performance Group')
    hist_values = grade['Age Stanine (AS) N'].value_counts().to_frame()
    hist_values.columns = ['Count']
    for i in [1,2,3,4,5,6,7,8,9]:
      if i in hist_values.index:
        continue
      else:
        hist_values.loc[i] = [0]
    hist_values.reset_index(inplace=True)
    hist_values = hist_values.rename(columns = {'index':'Performance Group'})
    hist_values['Performance Group'] = hist_values['Performance Group'].astype('Int64').astype(str)
    test = alt.Chart(hist_values).mark_bar().encode(
      x='Performance Group',
      y='Count',
      tooltip=['Count']
    )
    st.altair_chart(test, use_container_width=True)

if st.sidebar.checkbox('Show Raw Data'):
  grade

st.sidebar.image('stanine.png')

# Different Cut Scores for each school two sets, Bates and Chrysler and FLICS
# Grade level availability plays a role in the older grade levels
# Kindergarten comparison of Grade to Age rankings

#k_compare = cogat.loc[cogat['Age Stanine (AS) VN'].notnull()]
#k_compare['Grade/Age Difference'] = k_compare['Age Stanine (AS) VN'] -  k_compare['Grade Stanine (GS) VN']
#k_compare = k_compare['Grade/Age Difference'].value_counts()
#st.bar_chart(k_compare)