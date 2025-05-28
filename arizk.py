# -*- coding: utf-8 -*-
"""
Created on Wed Aug 28 15:32:46 2024

@author: Dell
"""
# packages
import streamlit as st
import pandas as pd
import numpy as np
from datetime import date, timedelta,datetime
from hubspot import HubSpot
from hubspot.crm.associations import BatchInputPublicObjectId
import altair as alt
############################################################################################################
# Global Variables
TOKEN = st.secrets["arizk_key"]
api_client = HubSpot(access_token=TOKEN)
objects_dict = {
    'deals': ['hubspot_owner_id', 'dealstage', 'description','amount','dealname','hs_deal_stage_probability',
                    'createdate','closedate', 'notes_last_contacted','hs_object_id'],
    'meetings': ['hubspot_owner_id','hs_timestamp','hs_object_id','hs_meeting_location','hs_meeting_outcome'],
    'companies': ['hubspot_owner_id', 'name','num_associated_contacts','num_associated_deals'],
    'tickets': ['hubspot_owner_id','hs_object_id','type','closed_date','content','time_to_close',
                'instrument','serial_number','subject','hs_file_upload','hs_pipeline_stage'],
    'tasks': ['hubspot_owner_id','hs_object_id','hs_task_subject','hs_task_status',
              'hs_timestamp','hs_task_completion_date'],
    'line_items':['name','hs_product_type']
    }
cols_dict = {
    'offers': ['User','dealname', 'Company', 'createdate', 'amount','Product',
               'ProductIDs'],
    'orders': ['User','dealname', 'Company', 'closedate','amount','Product',
               'ProductIDs'],
    'visits': ['User','Company','hs_timestamp','hs_meeting_outcome'],
    'tickets': ['User','type','closed_date'],
    'monthly': ['User','Company', 'description','dealname', 'createdate',
                'notes_last_contacted','Product','hs_deal_stage_probability','ProductIDs'],
    'tasks': ['User','hs_task_subject','hs_task_completion_date']
    }
cols_dict_renamed = {
    'offers': ['User','Offer No', 'Company', 'Date', 'Amount','Products',
               'ProductIDs'],
    'orders': ['User','Offer No', 'Company', 'Date','Amount','Products',
               'ProductIDs'],
    'visits': ['User','Company','Date','Meeting Outcome'],
    'tickets': ['User','Type','Date'],
    'monthly': ['User','Company', 'description','Offer No', 'Date',
                'Last Contacted Date','Products','Probability','ProductIDs'],
    'tasks': ['User','Subject','Date']
    }
status_dict = {
    'hs_pipeline_stage':['Closed'],
    'dealstage':['contractsent','closedwon'],
    'hs_task_status':['COMPLETED'],
    'hs_meeting_outcome':['COMPLETED']
    }
kpi_labels = ['Visits','Offers','Orders','Perform a Demo','Get bank Guarantee Back','Participate Marketing',
          'Make Your Own Webinar/Campaign/Conference', 'Attend Online Training/Webinar',
          'Obtain Product Training Certificate']
offer_categs = ['Density, Refractometer, Polarimeter, Contact Angle',
                'Viscosity, Rheology, Texture, Mixing, Extruders',
                'Fuel and Oil Properties',
                'Surface Properties: Surface Area, Porosity, Surpass, NanoIndention, NanoHardness, Scratch, XRD',
                'Particle Characteristics: Particle Size Analyzer, Zeta Potential, Litesizer, Milling',
                'Digestion, Elemental Analysis, XRF, TOC, CHNS, OCL, Raman, NIR, FTIR, OES',
                'Synthesis, Reactors, Fermentors, Biolin QCM-D, Moisture Analyzer',
                'Others (None of the above)']

ticket_stages = {
    '1':'New',
    '2':'Waiting on contact',
    '3':'Waiting on us',
    '835174392':'Waiting on supplier',
    '4':'Closed'
    }
dashboards = ['Weekly Dashboard','Monthly Dashboard','Tickets and Tasks']
############################################################################################################
#Methods:
def get_monthly_list(df):
    mlists = []
    for offer_categ in offer_categs:
        mlist = []
        for i in range(len(df)):
            deal = df.iloc[i]
            items_ids = deal['ProductIDs']
            items_categs = [line_items[line_items['hs_object_id']==items_id
                        ]['hs_product_type'].values for items_id in items_ids]
            if offer_categ in items_categs:
                deal = deal.iloc[:-1,]
                mlist.append(deal)
        mdf = pd.DataFrame(mlist).reset_index(drop=True)
        if len(mdf)>0:
            mdf = mdf.sort_values(by='Probability', ascending=False)
            mdf['Probability'] = np.round(mdf['Probability'])
            # mdf = mdf.head[5]
        mlists.append(mdf)
    return mlists

def get_tasks_values(df,toverdue):
    if len(df)>0:
       no_tasks_all = len(df)
       no_tasks_overdue = len(toverdue)
       no_closed_tasks = no_tasks_all - no_tasks_overdue
       ratio_close_tasks = str(int(round((no_closed_tasks/no_tasks_all)*100,0))) +' %' if no_tasks_all>0 else "NA"
       time_close_tasks = datetime.combine(date_until_selectbox, datetime.min.time()) - df['hs_timestamp'].dt.tz_localize(None)
       time_close_avg_tasks = int(round(np.mean(time_close_tasks.dt.days),0))
       time_close_avg_tasks_txt = str(int(round(np.mean(time_close_tasks.dt.days),0)))+" days" if no_closed_tasks >0 else "NA"
       time_close_avg_ratio_tasks = int(round(time_close_avg_tasks/no_closed_tasks,2)) if no_closed_tasks >0 else "NA"
       tasks_values = [no_tasks_all,no_tasks_overdue,ratio_close_tasks,time_close_avg_tasks_txt,time_close_avg_ratio_tasks]
    else:
       tasks_values = ['NA','NA','NA','NA','NA']
    return tasks_values

def get_tickets_values(df, topen):
    if len(df)>0:
        no_tickets_all = len(df)
        no_tickets_open = len(topen)
        no_closed_tickets = no_tickets_all - no_tickets_open
        ratio_close_ticket = str(int(round((no_closed_tickets / no_tickets_all)*100,0)))+' %' if no_tickets_all>0 else "NA"
        time_close_avg = int(round(df['time_to_close_days'].mean(),0)) 
        time_close_avg_txt = str(int(round(df['time_to_close_days'].mean(),0)))+" days" if no_closed_tickets >0 else "NA"
        time_close_avg_ratio = int(round(time_close_avg/no_closed_tickets,2)) if no_closed_tickets >0 else "NA"
        tickets_values = [no_tickets_all,no_tickets_open,ratio_close_ticket,time_close_avg_txt,time_close_avg_ratio]
    else:
        tickets_values = ['NA','NA','NA','NA','NA']
    return tickets_values

def get_selected_objects(obj_df,obj_key,obj_label):
    if obj_key == 'name':
        objs = list(obj_df.values())
    else:
        objs = list(obj_df[obj_key].dropna().unique())
    select_all_objs = st.checkbox('Select all '+obj_key+'s',value=True)
    if select_all_objs:
        selected_options = objs
    else:
        selected_options = []
    selections = st.multiselect(obj_label,objs, default=selected_options)
    return selections

# get associated companies
def batch_fetch_associations(obj_ids, obj_key, assoc_type):
    batch_ids = BatchInputPublicObjectId(inputs=[{'id': obj_id} for obj_id in obj_ids])
    associations = api_client.crm.associations.batch_api.read(
        from_object_type=obj_key,
        to_object_type=assoc_type,
        batch_input_public_object_id=batch_ids
        )
    return associations.results if associations.results else []

def get_associations(obj_ids, obj_key, associated_key):
    assoc_data = batch_fetch_associations(obj_ids, obj_key, associated_key)
    names = {obj_id: [] for obj_id in obj_ids}
    ids = {obj_id: [] for obj_id in obj_ids}
    if assoc_data:
        for assoc in assoc_data:
            assoc_id = assoc._from.id
            for obj in assoc.to:
                obj_id = obj.id
                if associated_key == 'companies':
                    obj_df = companies[companies['hs_object_id']==obj_id]
                else:
                    obj_df = line_items[line_items['hs_object_id']==obj_id]
                name = obj_df['name'].values if obj_df['name'].values else ""
                names[assoc_id].append(name)
                ids[assoc_id].append(obj_id)
    return names,ids

# get object properties df
def add_users_to_df(obj_df,obj_key):
    user_names = [users[user_id_value] for user_id_value in obj_df['hubspot_owner_id'].values]
    obj_df['User'] = user_names
    return obj_df

# get object properties df
def add_associations_to_df(obj_df,obj_key):
    obj_ids = obj_df['hs_object_id'].values
    company_names, company_ids = get_associations(obj_ids, obj_key, 'companies')
    obj_df['Company'] = obj_df['hs_object_id'].map(company_names)
    if obj_key == 'deals':
        product_names, product_ids = get_associations(obj_ids, obj_key, 'line_items')
        obj_df['Product'] = obj_df['hs_object_id'].map(product_names)
        obj_df['ProductIDs'] = obj_df['hs_object_id'].map(product_ids)
    obj_df = add_users_to_df(obj_df,obj_key)
    obj_ids = obj_df['hs_object_id'].values
    return obj_df.reset_index(drop=True)
############################################################################################################

# Get all data
def get_users():
    users_list = api_client.crm.owners.get_all()
    return {user.id:user.first_name + " " + user.last_name for user in users_list}

def get_df(obj_key):
    obj_df = pd.DataFrame()
    obj_list = api_client.crm.objects.get_all(object_type=obj_key, properties = objects_dict[obj_key])
    for obj in obj_list:
        obj_df = pd.concat([obj_df,pd.DataFrame(obj.properties, index = [0])])
    if obj_key =='tickets':
        obj_df['hs_pipeline_stage'] = obj_df['hs_pipeline_stage'].map(ticket_stages)
        obj_df['time_to_close_days'] = pd.to_numeric(obj_df['time_to_close'], errors='coerce')/86400000
    elif obj_key =='tasks':
        obj_df['hs_timestamp'] = pd.to_datetime(obj_df['hs_timestamp'])
    return obj_df.reset_index(drop=True)

def get_key_by_value(my_dict, target_value):
    for key, value in my_dict.items():
        if value == target_value:
            return key
    return None

def format_date_columns(df, date_column):
    df[date_column] = pd.to_datetime(df[date_column], 
                                     format='ISO8601', utc=True, errors='coerce'
                                     ).dt.strftime('%d.%m.%Y')
    return df

def filter_df(df,date_key,status_key,cols_key,dashboard_key,selected):
    if df.shape[0] >0: 
        if dashboard_key != '':
            status_value = status_dict[status_key][1] if cols_key=='orders' else status_dict[status_key][0]
            df = df[(df[date_key].between(start_date,end_date))&
                    (df[status_key]==status_value)]
        else:
            status_value = status_dict[status_key][0]
            df = df[(df[date_key]<end_date)&
                    (df[status_key]!=status_value)]
        df = df.loc[df['User'].isin(selected)]
    df = df[cols_dict[cols_key]]
    df.columns=cols_dict_renamed[cols_key]
    if date_key == 'notes_last_contacted':
        df = format_date_columns(df, 'Last Contacted Date')
    df = format_date_columns(df, 'Date')
    return df.reset_index(drop=True)

def calculate_kpi(df_offers,df_orders,df_visits,df_tickets,u_name):
    visits_ = len(df_visits[df_visits['User']==u_name])*10
    orders_ = len(df_orders[df_orders['User']==u_name])*10
    offers_ = len(df_offers[df_offers['User']==u_name])*10
    df_tickets_ = df_tickets[df_tickets['User']==u_name]
    demo = len(df_tickets_[df_tickets_['Type']=='Perform a Demo'])*20
    guarantee = len(df_tickets_[df_tickets_['Type']=='Get bank Guarantee Back'])*10
    part_marketing = len(df_tickets_[df_tickets_['Type']=='Participate Marketing'])*20
    make_marketing = len(df_tickets_[df_tickets_['Type']=='Make Your Own Webinar/Campaign/Conference'])*200
    attend_training = len(df_tickets_[df_tickets_['Type']=='Attend Online Training/Webinar'])*10
    certificates = len(df_tickets_[df_tickets_['Type']=='Obtain Product Training Certificate'])*200
    kpis = [visits_,offers_,orders_,demo,guarantee,part_marketing,make_marketing,attend_training,certificates]
    return kpis

def plot_user_comparison_bar_chart(df):
    """
    Plots a horizontal grouped bar chart comparing multiple properties across users.

    Parameters:
    df (pd.DataFrame): DataFrame where index is user names and columns are properties (metrics).
    """
    # Reset index so 'User' becomes a column
    df_reset = df.reset_index().rename(columns={'index': 'User'})
    
    # Melt to long format for Altair
    df_long = df_reset.melt(id_vars='User', var_name='Metric', value_name='Value')

    # Altair chart
    chart = alt.Chart(df_long).mark_bar().encode(
        x='Value:Q',
        y=alt.Y('User:N', sort='-x'),
        color='Metric:N',
        tooltip=['User:N', 'Metric:N', 'Value:Q']
    ).properties(
        title='User Activity Comparison'
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    )

    # Display chart in Streamlit
    st.altair_chart(chart, use_container_width=True)

# def get_bar_chart(categ,val):
#     if np.sum(val)>0:
#         data = pd.DataFrame(val,index=categ)
#         df = pd.melt(data.reset_index(), id_vars=["index"])
#         chart = (alt.Chart(df).mark_bar().encode(
#         x=alt.X("value", type="quantitative", title=""),
#         y=alt.Y("index", type="nominal", title=""),))
#         return st.altair_chart(chart, use_container_width=True)
############################################################################################################
# All Data
companies = get_df('companies')
line_items = get_df('line_items')
users = get_users()

if 'deals' not in st.session_state:
    st.session_state['deals'] = add_associations_to_df(get_df('deals'),'deals')
    st.session_state['meetings'] = add_associations_to_df(get_df('meetings'),'meetings')
    st.session_state['tickets'] = add_associations_to_df(get_df('tickets'),'tickets')
    st.session_state['tasks'] = add_associations_to_df(get_df('tasks'),'tasks')
deals = st.session_state['deals']
meetings = st.session_state['meetings']
tickets = st.session_state['tickets']
tasks = st.session_state['tasks']
############################################################################################################
# Layout
st.set_page_config(layout="wide")
# Side bar
dashboards_selectbox = st.sidebar.selectbox(
    "Select Dashboard",
    (dashboards)
)
date_from_selectbox = st.sidebar.date_input(
    "Date From",
    date.today() - timedelta(days=6)
)
date_until_selectbox = st.sidebar.date_input(
    "Date Until",
    date.today() + timedelta(days=1)
)
############################################################################################################
# Global Variables
start_date = str(date_from_selectbox)
end_date = str(date_until_selectbox)
############################################################################################################
# Weekly Dashboard
def get_weekly_dashboard():
    selected_users = get_selected_objects(users, 'name', 'Select user(s):')
    # Define Data
    offers_df = filter_df(deals,'createdate','dealstage','offers','weekly',selected_users)
    orders_df = filter_df(deals,'closedate','dealstage','orders','weekly',selected_users)
    visits_df = filter_df(meetings,'hs_timestamp','hs_meeting_outcome','visits','weekly',selected_users)
    tickets_df = filter_df(tickets,'closed_date','hs_pipeline_stage','tickets','weekly',selected_users)
    tasks_df = filter_df(tasks,'hs_task_completion_date','hs_task_status','tasks','weekly',selected_users)
    weekly_df_lists = [visits_df,offers_df,orders_df,tickets_df,tasks_df]
    weekly_df_labels = ['Visits','Offers','Orders','Closed Tickets','Completed Tasks']
    # Metrics Table
    kpi = []
    kpi_values = {}
    for s in selected_users:
        kpi_values[s] = calculate_kpi(offers_df,orders_df,visits_df,tickets_df,s)
        kpi.append(np.sum(kpi_values[s]))
    weekly_metrics_dict = {'KPI':kpi}
    for i in range(len(weekly_df_labels)):
        current_df = weekly_df_lists[i]
        current_df_counts = []
        for u in selected_users:
            current_u_counts = current_df['User'].value_counts().loc[u] if u in current_df['User'].value_counts() else 0
            current_df_counts.append(current_u_counts)
        weekly_metrics_dict[weekly_df_labels[i]] = current_df_counts
    weekly_metrics_df = pd.DataFrame(weekly_metrics_dict, index=selected_users)
    st.markdown("### Users Table")
    st.dataframe(weekly_metrics_df, use_container_width=True)
    
    # bar chart
    plot_user_comparison_bar_chart(weekly_metrics_df)
    
    # Tables
    for j in range(len(weekly_df_labels)):
        st.markdown("### "+weekly_df_labels[j])
        st.dataframe(weekly_df_lists[j], use_container_width=True)

def get_monthly_dashboard():
    selected_users = get_selected_objects(users, 'name', 'Select user(s):')
    monthly_df = filter_df(deals,'notes_last_contacted','dealstage','monthly','Monthly Dashboard',selected_users)
    monthly_df_list = get_monthly_list(monthly_df)
    score = 0 
    for i in range(len(monthly_df_list)):
        score += len(monthly_df_list[i])
    # score += [len(monthly_df_list[i]) for i in monthly_df_list]
    st.markdown("#### Score = "+str(round(score*100/40))+"%")
    # st.markdown("### Users Table")
    for k in range(len(offer_categs)):
        st.markdown("### "+offer_categs[k])
        st.dataframe(monthly_df_list[k], use_container_width=True)

def get_tickets_dashboard():
    selected_users = get_selected_objects(users, 'name', 'Select user(s):')
    # tickets metrics
    selected_tickets = get_selected_objects(tickets, 'type','Select ticket type(s):')
    tickets_filtered = tickets.loc[tickets['type'].isin(selected_tickets)]
    tickets_open = filter_df(tickets_filtered, 'createdate', 'hs_pipeline_stage', 'tickets', '',selected_users)
    tickets_filtered = tickets_filtered.loc[tickets_filtered['User'].isin(selected_users)]
    tickets_values = get_tickets_values(tickets_filtered,tickets_open)
    tickets_labels = ['All Tickets','All Open Tickets','Closed Tickets Ratio','Avg Close T Tickets','Avg Close T Ratio Tickets']
    # tickets_metrics = st.columns(5,gap="small") 
    # for i in range(len(tickets_values)):
    #     tickets_metrics[i].metric(label='# '+tickets_labels[i],value=tickets_values[i])  
    # table tickets
    tickets_dict = {}
    for k in range(len(tickets_values)):
        tickets_counts = []
        for u in range(len(selected_users)):
            tickets_filtered_ = tickets_filtered[tickets_filtered['User']==selected_users[u]]
            tickets_open_ = tickets_open[tickets_open['User']==selected_users[u]]
            tickets_counts.append(get_tickets_values(tickets_filtered_,tickets_open_)[k])
        tickets_dict[tickets_labels[k]] = tickets_counts
    tickets_metrics_df = pd.DataFrame(tickets_dict, index=selected_users)
    st.markdown("### Users Tickets")
    st.dataframe(tickets_metrics_df, use_container_width=True)
    # tasks metrics
    tasks_ = tasks.loc[tasks['User'].isin(selected_users)]
    tasks_overdue = filter_df(tasks_, 'hs_timestamp', 'hs_task_status', 'tasks', '',selected_users)
    tasks_values = get_tasks_values(tasks_,tasks_overdue)
    tasks_labels = ["All Tasks","All Overdue Tasks","Closed Tasks Ratio","Avg Close T Tasks","Avg Close T Ratio Tasks"]
    # tasks_metrics = st.columns(5,gap="small")
    # for j in range(len(tasks_values)):
    #     tasks_metrics[j].metric(label='# '+tasks_labels[j],value=tasks_values[j]) 
    tasks_dict = {}
    for l in range(len(tasks_values)):
        tasks_counts = []
        for us in range(len(selected_users)):
            tasks_filtered_ = tasks_[tasks_['User']==selected_users[us]]
            tasks_overdue_ = tasks_overdue[tasks_overdue['User']==selected_users[us]]
            tasks_counts.append(get_tasks_values(tasks_filtered_,tasks_overdue_)[l])
        tasks_dict[tasks_labels[l]] = tasks_counts
    tasks_metrics_df = pd.DataFrame(tasks_dict, index=selected_users)
    st.markdown("### Users Tasks")
    st.dataframe(tasks_metrics_df, use_container_width=True)
    # tables
    if len(tickets_filtered)>0:        
        st.markdown("### All Open Tickets")
        st.dataframe(tickets_open, use_container_width=True)
    if len(tasks_)>0: 
        st.markdown("### All Overdue Tasks")
        st.dataframe(tasks_overdue, use_container_width=True)

if dashboards_selectbox == 'Weekly Dashboard':
    get_weekly_dashboard()
elif dashboards_selectbox == 'Monthly Dashboard':
    get_monthly_dashboard()
else: 
    get_tickets_dashboard()
