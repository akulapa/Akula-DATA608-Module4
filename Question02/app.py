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
df = pd.read_csv('https://raw.githubusercontent.com/akulapa/Akula-DATA608-Module4/master/Question02/riverkeeper_data_2013.csv')

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
df['FourDayRainTotal'] = df['FourDayRainTotal'].values.astype(np.float64)
df['Enterococcus Count'] = df['EnteroCount'].values.astype(np.int64)
df['Four Day Rain Total'] = df['FourDayRainTotal'].values.astype(np.float64)

df['Dt'] = pd.to_datetime(df.Date)
df = df.sort_values(by=['Dt'],ascending=0)

dfFull = df
df = df[['Site','EnteroCount',"FourDayRainTotal"]]
sites = df.Site.unique()

#overAlldf = df[['EnteroCount',"FourDayRainTotal"]]
#overAllCorDf = overAlldf.corr()
#eCorDf = overAllCorDf[overAllCorDf['EnteroCount'] != 1]
#eCorVal = eCorDf['EnteroCount']
#eCorVal = round(float(eCorVal),3)
#msg1 = 'Overall Correlation Between Enterococcus Count And Rainfal: ' + str(eCorVal)

app = dash.Dash()

app.layout = html.Div([
    html.H3('Water Quality Information System'),
    html.H4('Correlation Between Enterococcus Count And Rainfall At Each Site'),
    dcc.Dropdown(
        id='field-dropdown',
        options=[{'label': s, 'value': s} for s in sites],
        value=sites[0],
        clearable=False
    ),
    dtbl.DataTable(
        # Initialise the rows
        rows=[{}],
        row_selectable=False,
        filterable=False,
        sortable=False,
        editable=False,
        selected_row_indices=[],
        id='table'
        ),
    html.H4('Samples Collected'),
    dtbl.DataTable(
        # Initialise the rows
        rows=[{}],
        row_selectable=False,
        filterable=False,
        sortable=False,
        editable=False,
        selected_row_indices=[],
        id='table1'
        )
])

@app.callback(
    dash.dependencies.Output('table', 'rows'),
    [dash.dependencies.Input('field-dropdown', 'value')])
def update_site(site):
    infoDf = pd.DataFrame()
    
    #Filter by site
    siteFulldf = dfFull[dfFull['Site'] == site]
    siteDf = df[df['Site'] == site]
    #Calculate correlation
    siteCorDf = siteDf.corr()
    eCorDf = siteCorDf[siteCorDf['EnteroCount'] != 1]
    eCorVal = eCorDf['EnteroCount']
    eCorVal = float(eCorVal)
    #Get geometric mean
    gMean = stats.gmean(siteDf.loc[:,"EnteroCount"])
    #Avg rainfall at the site
    avgRain = siteDf['FourDayRainTotal'].mean()
    #Last time sample was collected
    lastSample = max(pd.to_datetime(siteFulldf.Date))
    
    data = {'Site':site, 'Correlation Coefficient':round(eCorVal,3), 'Geo.Mean Enterococcus Count':round(gMean,3), 'Avg. Rainfall':round(avgRain,3), 'Last Sample Date':lastSample.strftime('%m/%d/%Y')}
    infoDf = infoDf.append(data, ignore_index=True)
    
    if (len(infoDf) == 0):
        data = {'Site':'', 'Correlation Coefficient':'', 'Geo.Mean Enterococcus Count':'', 'Avg. Rainfall':'', 'Last Sample Date':''}
        infoDf = infoDf.append(data, ignore_index=True)
    
    cols = ['Site', 'Correlation Coefficient', 'Geo.Mean Enterococcus Count', 'Avg. Rainfall', 'Last Sample Date']
    infoDf = infoDf[cols]
    return(infoDf.to_dict('records'))
    
@app.callback(
    dash.dependencies.Output('table1', 'rows'),
    [dash.dependencies.Input('field-dropdown', 'value')])
def update_details(site):
    
    #Filter by site
    siteFulldf = dfFull[dfFull['Site'] == site]
    
    siteFulldf = siteFulldf[['Site','Date', 'Enterococcus Count',"Four Day Rain Total"]]
    
    cols = ['Site','Date', 'Enterococcus Count',"Four Day Rain Total"]
    siteFulldf = siteFulldf[cols]
    return(siteFulldf.to_dict('records'))
    
if __name__ == '__main__':
    app.run_server(debug=True)