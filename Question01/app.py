# -*- coding: utf-8 -*-
"""
Created on Sun Mar 25 13:34:39 2018

@author: akulap
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import numpy as np
from datetime import datetime as dt
import datetime
import dash_table_experiments as dtbl
from scipy import stats

def numericEC(ec):
    validEC = False
    try:
        qty = int(ec)
        if qty >= 0:
            validEC = True
    except ValueError:
        validEC = False
    return validEC


#df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminderDataFiveYear.csv')
#Read data
df = pd.read_csv('D:/CUNY/608/Project04/riverkeeper_data_2013.csv')

#Remove < and > signs and tidy data
for idx in df.index:
    ec = df.get_value(idx, 'EnteroCount')
    if not numericEC(ec):
        ec = ec.replace(">", "")
        if not numericEC(ec):
            ec = ec.replace("<", "")
            if numericEC(ec):
                ec = int(ec) - 1
                if ec < 0:
                    ec = 0
        else:
            ec = int(ec) + 1
    df.set_value(idx, 'EnteroCount', ec)

#Convert EnteroCount to int
df['EnteroCount'] = df['EnteroCount'].values.astype(np.int64)
df['Entero Count'] = df['EnteroCount']
df['Dt'] = pd.to_datetime(df.Date)

df = df.sort_values(by=['Dt'],ascending=0)
#Get distinct dates
sDates = df.Date.unique()

app = dash.Dash()

app.layout = html.Div([
    html.H3('Water Quality Information System'),
    dcc.Dropdown(
        id='field-dropdown',
        options=[{'label': d, 'value': d} for d in sDates],
        value=sDates[0],
        clearable=False
    ),
     html.Div(id='river-info'),
     html.Div([   dtbl.DataTable(
        # Initialise the rows
        rows=[{}],
        row_selectable=False,
        filterable=False,
        sortable=False,
        editable=False,
        selected_row_indices=[],
        id='table'
    )
    ])
])


@app.callback(
    dash.dependencies.Output('river-info', 'children'),
    [dash.dependencies.Input('field-dropdown', 'value')])
def select_info(date):
    return('Data collected on OR before: {}'.format(date))

@app.callback(
    dash.dependencies.Output('table', 'rows'),
    [dash.dependencies.Input('field-dropdown', 'value')])
def update_date(date):
    retdf = pd.DataFrame()
    if date is not None:
        sdate = pd.to_datetime(date)
        #Filter on Date
        sfiltered = df[df['Dt'] <= sdate]
        sSites = sfiltered.Site.unique()
        #Loop through each site
        for site in sSites:
            #Filter by site
            cSite = sfiltered[sfiltered['Site'] == site]
            #Get last sample date
            lastSample = max(pd.to_datetime(cSite.Date))
            lastSample = pd.to_datetime(lastSample)
            eMaxDf = cSite[cSite['Dt'] == lastSample]
            eMax = max(eMaxDf['EnteroCount'])
            
            #Check last sample
            if eMax > 110:
                msg1 = "Single Sample > 110"
                msg2 = "N"
                
            #Check Geometric mean
            if ((len(cSite) >= 5) and (eMax <= 110)):
                gMean = stats.gmean(cSite.loc[:,"EnteroCount"])
                if gMean > 30:
                    msg1 = "Geometric Mean > 30"
                    msg2 = "N"
                else:
                    msg1 = "Single Sample < 110 And Geometric Mean < 30"
                    msg2 = "Y"

            #Mark it safe
            if ((len(cSite) < 5) and (eMax <= 110)):
                    msg1 = "Single Sample < 110 And Geometric Mean < 30"
                    msg2 = "Y"

            data = {'Site':site, 'Enterococcus Count':msg1, 'Safe To Kayak':msg2, 'Last Sample Date':lastSample.strftime('%m/%d/%Y')}
            retdf = retdf.append(data, ignore_index=True)
    
    if (len(retdf) == 0):
        data = {'Site':'', 'Enterococcus Count':'', 'Safe To Kayak':'', 'Last Sample Date':''}
        retdf = retdf.append(data, ignore_index=True)

    cols = ['Site','Enterococcus Count','Safe To Kayak','Last Sample Date']
    retdf = retdf[cols]
    return(retdf.to_dict('records'))

#@app.callback(
#    dash.dependencies.Output('table', 'rows'),
#    [dash.dependencies.Input('field-dropdown', 'value')])
#def update_dropdown(site):
#    """
#    For user selections, return the relevant table
#    """
#    filtered = df[df['Site'] == site]
#    return(filtered.to_dict('records'))


if __name__ == '__main__':
    app.run_server(debug=True)