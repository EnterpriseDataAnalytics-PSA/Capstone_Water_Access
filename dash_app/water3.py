import dash
import dash_core_components as dcc
import dash_html_components as html
import datetime
from collections import deque
import plotly.graph_objs as go
import psycopg2
import pandas as pd
from dash.dependencies import Output, Event, Input, State
import dash_table_experiments as dt
try:
    from urllib.parse import urlparse
except ImportError:
     from urlparse import urlparse


#get rid of lat lon from the table - moved to the back
#predictions yes no instead of 0's and 1's
#color code based on today's prediction - done
#table columns - order - done
#Status_id should not be used - use status_binary

#function for colors
def color_col(x):
    if x == "yes":
        return "rgb(0,255,0)"
    if x == "no":
        return "rgb(255,0,0)"
    if x == "unknown":
        return "rgb(255, 153, 51)"

def color_col_pred(x):
    if x == "Not Working":
        return "rgb(255,0,0)"
    if x == "Working":
        return "rgb(0,255,0)"



## Connect and pull initial df
conn = psycopg2.connect("dbname='water_db' user='dan' host='postgres-instance2.clhlqrsuvowr.us-east-1.rds.amazonaws.com' password='berkeley'")
query = "SELECT country_name, district, sub_district, status_id, fuzzy_water_source, fuzzy_water_tech, management, today_preds_text, one_year_preds_text, one_km_population, lat_deg, lon_deg from final_all WHERE country_name = 'Kenya'"
df_init = pd.read_sql_query(query, conn)
df_init["color"] = df_init["today_preds_text"].apply(color_col_pred)
conn.close()
mapbox_access_token = 'pk.eyJ1IjoiZHdhdHNvbjgyOCIsImEiOiJjamVycHp0b3cxY2dyMnhsdGc4eHBkcW85In0.uGPxMK4_u-nAs_J74yw70A'

## query for countries, districts, subdistricts
conn = psycopg2.connect("dbname='water_db' user='dan' host='postgres-instance2.clhlqrsuvowr.us-east-1.rds.amazonaws.com' password='berkeley'")
q2 = "SELECT * FROM menu_table"
df2 = pd.read_sql_query(q2, conn)
conn.close()
### Color Scale



## insertion point for css and js
external_css = [
    'https://codepen.io/chriddp/pen/bWLwgp.css',
    'https://api.tiles.mapbox.com/mapbox-gl-js/v0.44.1/mapbox-gl.css',
    'https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css'
]

external_js = [
    'https://api.tiles.mapbox.com/mapbox-gl-js/v0.44.1/mapbox-gl.js',
    'https://code.jquery.com/jquery-3.2.1.slim.min.js',
    'https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js'
]

def generate_table(dataframe):
    return dt.DataTable(
        id='filter-table',
        rows=dataframe.to_dict('records'),

        # optional - sets the order of columns
        columns=dataframe.columns,

        row_selectable=True,
        filterable=True,
        sortable=True,
        selected_row_indices=[],
    )


app = dash.Dash()
app.title = "water site"
##JS and CSS app integration
for js in external_js:
    app.scripts.append_script({'external_url': js})

for css in external_css:
    app.css.append_css({'external_url': css})



app.layout = html.Div([
    # Column: Title + Map
        # Row: Title
        html.Div([
        # Row: Map
        html.Div([
        dcc.Dropdown(className = "dropdown", id = 'country-select',
            options=[
            {'label': i, 'value': i} for i in df2.country_name.sort_values().unique()],
             #value = df2.country_name."sort_values().unique()[0], 
            placeholder = "Select a Country",
            value = "Kenya"      
        ),
        ], style = {"padding":"5px"}),
        html.Div([
        dcc.Dropdown(className = "dropdown", id = 'district-select',
            options=[
            {'label': i, 'value': i} for i in df2.district.sort_values().unique()],
            placeholder = "Select a District",
            multi = True     
        ),
        ], style = {"padding":"5px"}),
        html.Div([
        dcc.Dropdown(id = 'sub-district-select',
            options = [
            {'label': i, 'value': i} for i in df2.sub_district.sort_values().unique()],
            placeholder = 'Select a Sub-District',
            multi = True
        ),
        ], style = {"padding":"5px"}),
        html.Div([
        dcc.Dropdown(id = 'status-select',
            options = [
            {'label': i, 'value': i} for i in df2.status_id.sort_values().unique()],
            placeholder = "Last known status",
            multi = True
        ),
        ], style = {"padding":"5px"}),
        #fix to update only to available
        html.Div([
        dcc.Dropdown(id = 'watersource-select',
            options=[
             {'label': i, 'value': i} for i in df2.fuzzy_water_source.sort_values().unique()],
             #value = df_init.fuzzy_water_source.sort_values().unique()[0:2], 
             placeholder = "Select a Water Source",
             multi= True       
        ),
        ], style = {"padding":"5px"}),
        #fix to update only to available
        html.Div([
        dcc.Dropdown(id = 'watertech-select',
            options=[
             {'label': i, 'value': i} for i in df2.fuzzy_water_tech.sort_values().unique()],
             #value = df_init.fuzzy_water_tech.sort_values().unique()[0:2], 
             placeholder = "Select a Water Tech",
             multi = True       
        ),
        ], style = {"padding":"5px"}),
        #Fix to update only to available
        html.Div([
        dcc.Dropdown(id = 'management-select',
            options=[
             {'label': i, 'value': i} for i in df2.management.sort_values().unique()],
             #value =  df_init.management.sort_values().unique()[0:2],
             placeholder = "Select Water Point Management",
             multi = True       
        ),
        ], style = {"padding":"5px"}),
        html.Div([
        dcc.Dropdown(id = 'today-pred-select',
            options=[
             {'label': i, 'value': i} for i in df2.today_preds_text.sort_values().unique()],
             placeholder = "Select Today's Prediction",
             multi = True       
        ),
        ], style = {"padding":"5px"}),
        html.Div([
        dcc.Dropdown(id = 'one-year-pred-select',
            options=[
             {'label': i, 'value': i} for i in df2.one_year_preds_text.sort_values().unique()],
             placeholder = "Select One year Prediction",
             multi = True       
        ),
        ], style = {"padding":"5px"}),
        html.Div([
        html.Button('submit', id= 'submit-button'),
        ], style = {"padding":"5px"}),
        html.Div([
        html.A('Download Data', id= 'download-link', download ="waterpoint_data.csv", href="", target= "_blank"),
        ]),
        ], className="col-md-4"),
    
    html.Div([
        dcc.Graph(id = "output-graph",
        figure ={"data": [
                {
                    "type": "scattermapbox",
                    "lat": df_init.lat_deg,
                    "lon": df_init.lon_deg,
                    "text": df_init.today_preds_text,
                    "cluster": True,
                    "mode": "markers",
                    "marker": {
                        "size": 8,
                        "opacity": 1.0,
                        "color" : df_init['color'] 
                    }
                }
            ],
        "layout": {
            "autosize": True,
            "hovermode": "closest",
            "mapbox": {
                "accesstoken": mapbox_access_token,
                "center": {
                    "lat": df_init.lat_deg.mean(),
                    "lon": df_init.lon_deg.mean()
                },
                "cluster": True,
                "pitch": 0,
                "zoom": 4,
                "style": "outdoors"
            }
        }
    })
    ], className="col-md-8", style = {'border':'1px solid black'}),
    html.H6(children = "", id = "well_text"),
    html.Div([
        generate_table(df_init)
        ], className="col-md-12", style = {"font-size":"small"}),

], className="container-fluid row")



## Update graph with query from filters above
@app.callback(Output('output-graph', 'figure'), [Input('submit-button', 'n_clicks')], state= [State('country-select', 'value'),
 State('status-select', 'value'), State('district-select', 'value'), State('sub-district-select', 'value'), State('watersource-select', 'value'), State('watertech-select', 'value'),
 State('management-select', 'value'), State('today-pred-select', 'value'), State('one-year-pred-select', 'value')])
def run_query(n_clicks, country, status, district, sub_district, fuzzy_water_source, fuzzy_water_tech, management, today_preds_text, one_year_preds_text):
    conn = psycopg2.connect("dbname='water_db' user='dan' host='postgres-instance2.clhlqrsuvowr.us-east-1.rds.amazonaws.com' password='berkeley'")
    base_query = "SELECT lat_deg, lon_deg, status_id, today_preds_text from final_all WHERE country_name =" + "'" + str(country) + "'"


    if not status:
        pass
    else:
        base_query = base_query + " and status_id in (" + ', '.join("'" + i + "'" for i in status) + ")"

    if not district:
        pass
    else:
        base_query = base_query +" and district in (" + ', '.join("'" + i + "'" for i in district) + ")"

    if not sub_district:
        pass
    else:
        base_query = base_query +" and sub_district in (" + ', '.join("'" + i + "'" for i in sub_district) + ")"

    if not fuzzy_water_source:
        pass
    else:
        base_query = base_query +" and fuzzy_water_source in (" + ', '.join("'" + i + "'" for i in fuzzy_water_source) + ")"

    if not fuzzy_water_tech:
        pass
    else:
        base_query = base_query +" and fuzzy_water_tech in (" + ', '.join("'" + i + "'" for i in fuzzy_water_tech) + ")"

    if not management:
        pass
    else:
        base_query = base_query +" and management in (" + ', '.join("'" + i + "'" for i in management) + ")"

    if not today_preds_text:
        pass
    else:
        base_query = base_query +" and today_preds_text in (" + ', '.join("'" + i + "'" for i in today_preds_text) + ")"

    if not one_year_preds_text:
        pass
    else:
        base_query = base_query +" and one_year_preds_text in (" + ', '.join("'" + i + "'" for i in one_year_preds_text) + ")"


    df = pd.read_sql_query(base_query, conn)
    df["color"] = df["today_preds_text"].apply(color_col_pred)
    conn.close()
    mapbox_access_token = 'pk.eyJ1IjoiZHdhdHNvbjgyOCIsImEiOiJjamVycHp0b3cxY2dyMnhsdGc4eHBkcW85In0.uGPxMK4_u-nAs_J74yw70A'
    figure = { "data": [
                {
                    "type": "scattermapbox",
                    "lat": df.lat_deg,
                    "lon": df.lon_deg,
                    "text": df.today_preds_text,

                    "mode": "markers",
                    "marker": {
                        "size": 8,
                        "opacity": .8,
                        "color" : df['color']                        
                    }
                }
            ],
        "layout": {
            "autosize": True,
            "hovermode": "closest",
            "mapbox": {
                "accesstoken": mapbox_access_token,
                "center": {
                    "lat": df.lat_deg.mean(),
                    "lon": df.lon_deg.mean()
                },
                "pitch": 0,
                "zoom": 4,
                "style": "outdoors",
                "cluster": True,
            }
        }
    }
    return figure

## Update table with query from filters above
@app.callback(Output('filter-table', 'rows'), [Input('submit-button', 'n_clicks')], state= [State('country-select', 'value'),
 State('status-select', 'value'), State('district-select', 'value'), State('sub-district-select', 'value'), State('watersource-select', 'value'), State('watertech-select', 'value'),
 State('management-select', 'value'), State('today-pred-select', 'value'), State('one-year-pred-select', 'value')])
def run_query(n_clicks, country, status, district, sub_district, fuzzy_water_source, fuzzy_water_tech, management, today_preds_text, one_year_preds_text):
    conn = psycopg2.connect("dbname='water_db' user='dan' host='postgres-instance2.clhlqrsuvowr.us-east-1.rds.amazonaws.com' password='berkeley'")
    base_query = "SELECT country_name, district, sub_district, status_id, fuzzy_water_source, fuzzy_water_tech, management,  today_preds_text, one_year_preds_text, one_km_population, lat_deg, lon_deg from final_all WHERE country_name =" + "'" + str(country) + "'"


    if not status:
        pass
    else:
        base_query = base_query + " and status_id in (" + ', '.join("'" + i + "'" for i in status) + ")"

    if not district:
        pass
    else:
        base_query = base_query +" and district in (" + ', '.join("'" + i + "'" for i in district) + ")"

    if not sub_district:
        pass
    else:
        base_query = base_query +" and sub_district in (" + ', '.join("'" + i + "'" for i in sub_district) + ")"

    if not fuzzy_water_source:
        pass
    else:
        base_query = base_query +" and fuzzy_water_source in (" + ', '.join("'" + i + "'" for i in fuzzy_water_source) + ")"

    if not fuzzy_water_tech:
        pass
    else:
        base_query = base_query +" and fuzzy_water_tech in (" + ', '.join("'" + i + "'" for i in fuzzy_water_tech) + ")"

    if not management:
        pass
    else:
        base_query = base_query +" and management in (" + ', '.join("'" + i + "'" for i in management) + ")"

    if not today_preds_text:
        pass
    else:
        base_query = base_query +" and today_preds_text in (" + ', '.join("'" + i + "'" for i in today_preds_text) + ")"

    if not one_year_preds_text:
        pass
    else:
        base_query = base_query +" and one_year_preds_text in (" + ', '.join("'" + i + "'" for i in one_year_preds_text) + ")"


    df = pd.read_sql_query(base_query, conn)
    conn.close()
    return df.to_dict('records')

##Download Button

@app.callback(Output('download-link', 'href'), [Input('filter-table', 'rows')])
def update_link(value):
    return '/dash/urlToDownload?value={}'.format(value)

@app.server.route('/dash/urlToDownload') 
def download_csv():
    value = flask.request.args.get('value')
    # create a dynamic csv or file here using `StringIO` 
    # (instead of writing to the file system)
    strIO = StringIO.StringIO()
    strIO.write('You have selected {}'.format(value)) 
    strIO.seek(0)    
    return send_file(strIO,
                     mimetype='text/csv',
                     attachment_filename='downloadFile.csv',
                     as_attachment=True)

## Update well_text for number of water points
@app.callback(Output("well_text", 'children'), [Input('filter-table', 'rows')])
def update_well_text(rows):
    return "Filters matched {} results".format(str(len(rows)))


########################################################################################################################################################################
##update districts menu
########################################################################################################################################################################
@app.callback(Output('district-select', 'options'), [Input('country-select', 'value'), Input('sub-district-select', 'value'),
    Input('status-select', 'value'), Input('watersource-select', 'value'), Input('watertech-select', 'value'), Input('management-select', 'value'),
    Input('today-pred-select', 'value'), Input('one-year-pred-select', 'value')])
def update_district(country, sub_district, status, fuzzy_water_source, fuzzy_water_tech, management, today_preds_text, one_year_preds_text):
    conn = psycopg2.connect("dbname='water_db' user='dan' host='postgres-instance2.clhlqrsuvowr.us-east-1.rds.amazonaws.com' password='berkeley'")
    base_query = "SELECT district from menu_table WHERE country_name =" + "'" + str(country) + "'"

    if not status:
        pass
    else:
        base_query = base_query + " and status_id in (" + ', '.join("'" + i + "'" for i in status) + ")"

    if not sub_district:
        pass
    else:
        base_query = base_query +" and sub_district in (" + ', '.join("'" + i + "'" for i in sub_district) + ")"

    if not fuzzy_water_source:
        pass
    else:
        base_query = base_query +" and fuzzy_water_source in (" + ', '.join("'" + i + "'" for i in fuzzy_water_source) + ")"

    if not fuzzy_water_tech:
        pass
    else:
        base_query = base_query +" and fuzzy_water_tech in (" + ', '.join("'" + i + "'" for i in fuzzy_water_tech) + ")"

    if not management:
        pass
    else:
        base_query = base_query +" and management in (" + ', '.join("'" + i + "'" for i in management) + ")"

    if not today_preds_text:
        pass
    else:
        base_query = base_query +" and today_preds_text in (" + ', '.join("'" + i + "'" for i in today_preds_text) + ")"

    if not one_year_preds_text:
        pass
    else:
        base_query = base_query +" and one_year_preds_text in (" + ', '.join("'" + i + "'" for i in one_year_preds_text) + ")"

    df = pd.read_sql_query(base_query, conn)
    conn.close()
    return [{'label': i, 'value': i} for i in df.district.sort_values().unique()]


##making sure that we clear input if country is none
@app.callback(Output('district-select', 'value'), [Input('country-select', 'value')])
def update_district(country):
    if country is None:
        return None

########################################################################################################################################################################
##update subdistricts menu
########################################################################################################################################################################

@app.callback(Output('sub-district-select', 'options'), [Input('country-select', 'value'), Input('district-select', 'value'),
    Input('status-select', 'value'), Input('watersource-select', 'value'), Input('watertech-select', 'value'), Input('management-select', 'value'),
    Input('today-pred-select', 'value'), Input('one-year-pred-select', 'value')])
def update_subdistrict(country, district, status, fuzzy_water_source, fuzzy_water_tech, management, today_preds_text, one_year_preds_text):
    conn = psycopg2.connect("dbname='water_db' user='dan' host='postgres-instance2.clhlqrsuvowr.us-east-1.rds.amazonaws.com' password='berkeley'")
    base_query = "SELECT sub_district from menu_table WHERE country_name =" + "'" + str(country) + "'"

    if not status:
        pass
    else:
        base_query = base_query + " and status_id in (" + ', '.join("'" + i + "'" for i in status) + ")"

    if not district:
        pass
    else:
        base_query = base_query +" and district in (" + ', '.join("'" + i + "'" for i in district) + ")"

    if not fuzzy_water_source:
        pass
    else:
        base_query = base_query +" and fuzzy_water_source in (" + ', '.join("'" + i + "'" for i in fuzzy_water_source) + ")"

    if not fuzzy_water_tech:
        pass
    else:
        base_query = base_query +" and fuzzy_water_tech in (" + ', '.join("'" + i + "'" for i in fuzzy_water_tech) + ")"

    if not management:
        pass
    else:
        base_query = base_query +" and management in (" + ', '.join("'" + i + "'" for i in management) + ")"

    if not today_preds_text:
        pass
    else:
        base_query = base_query +" and today_preds_text in (" + ', '.join("'" + i + "'" for i in today_preds_text) + ")"

    if not one_year_preds_text:
        pass
    else:
        base_query = base_query +" and one_year_preds_text in (" + ', '.join("'" + i + "'" for i in one_year_preds_text) + ")"

    df = pd.read_sql_query(base_query, conn)
    conn.close()
    return [{'label': i, 'value': i} for i in df.sub_district.sort_values().unique()]

##making sure that we clear input if country is none
@app.callback(Output('sub-district-select', 'value'), [Input('district-select', 'value'), Input('country-select', 'value')])
def update_subdistrict(district, country):
    if not district:
        return None
    if not country:
        return None

########################################################################################################################################################################
##update status
########################################################################################################################################################################
@app.callback(Output('status-select', 'options'), [Input('country-select', 'value'), Input('district-select', 'value'),
    Input('sub-district-select', 'value'), Input('watersource-select', 'value'), Input('watertech-select', 'value'), Input('management-select', 'value'),
    Input('today-pred-select', 'value'), Input('one-year-pred-select', 'value')])
def update_status(country, district, sub_district, fuzzy_water_source, fuzzy_water_tech, management, today_preds_text, one_year_preds_text):
    conn = psycopg2.connect("dbname='water_db' user='dan' host='postgres-instance2.clhlqrsuvowr.us-east-1.rds.amazonaws.com' password='berkeley'")
    base_query = "SELECT status_id from menu_table WHERE country_name =" + "'" + str(country) + "'"

    if not sub_district:
        pass
    else:
        base_query = base_query + " and sub_district in (" + ', '.join("'" + i + "'" for i in sub_district) + ")"

    if not district:
        pass
    else:
        base_query = base_query +" and district in (" + ', '.join("'" + i + "'" for i in district) + ")"

    if not fuzzy_water_source:
        pass
    else:
        base_query = base_query +" and fuzzy_water_source in (" + ', '.join("'" + i + "'" for i in fuzzy_water_source) + ")"

    if not fuzzy_water_tech:
        pass
    else:
        base_query = base_query +" and fuzzy_water_tech in (" + ', '.join("'" + i + "'" for i in fuzzy_water_tech) + ")"

    if not management:
        pass
    else:
        base_query = base_query +" and management in (" + ', '.join("'" + i + "'" for i in management) + ")"

    if not today_preds_text:
        pass
    else:
        base_query = base_query +" and today_preds_text in (" + ', '.join("'" + i + "'" for i in today_preds_text) + ")"

    if not one_year_preds_text:
        pass
    else:
        base_query = base_query +" and one_year_preds_text in (" + ', '.join("'" + i + "'" for i in one_year_preds_text) + ")"

    df = pd.read_sql_query(base_query, conn)
    conn.close()
    return [{'label': i, 'value': i} for i in df.status_id.sort_values().unique()]

#clearing
@app.callback(Output('status-select', 'value'), [Input('district-select', 'value'), Input('country-select', 'value'), Input('sub-district-select', 'value')])
def update_status(district_name, country, sub_district):
    if district_name is None:
        return None
    if sub_district is None:
        return None

########################################################################################################################################################################
##update water source
########################################################################################################################################################################    
@app.callback(Output('watersource-select', 'options'), [Input('country-select', 'value'), Input('district-select', 'value'),
    Input('sub-district-select', 'value'), Input('status-select', 'value'), Input('watertech-select', 'value'), Input('management-select', 'value'),
    Input('today-pred-select', 'value'), Input('one-year-pred-select', 'value')])
def update_watersource(country, district, sub_district, status, fuzzy_water_tech, management, today_preds_text, one_year_preds_text):
    conn = psycopg2.connect("dbname='water_db' user='dan' host='postgres-instance2.clhlqrsuvowr.us-east-1.rds.amazonaws.com' password='berkeley'")
    base_query = "SELECT fuzzy_water_source from menu_table WHERE country_name =" + "'" + str(country) + "'"

    if not sub_district:
        pass
    else:
        base_query = base_query + " and sub_district in (" + ', '.join("'" + i + "'" for i in sub_district) + ")"

    if not district:
        pass
    else:
        base_query = base_query +" and district in (" + ', '.join("'" + i + "'" for i in district) + ")"

    if not status:
        pass
    else:
        base_query = base_query +" and status_id in (" + ', '.join("'" + i + "'" for i in status) + ")"

    if not fuzzy_water_tech:
        pass
    else:
        base_query = base_query +" and fuzzy_water_tech in (" + ', '.join("'" + i + "'" for i in fuzzy_water_tech) + ")"

    if not management:
        pass
    else:
        base_query = base_query +" and management in (" + ', '.join("'" + i + "'" for i in management) + ")"

    if not today_preds_text:
        pass
    else:
        base_query = base_query +" and today_preds_text in (" + ', '.join("'" + i + "'" for i in today_preds_text) + ")"

    if not one_year_preds_text:
        pass
    else:
        base_query = base_query +" and one_year_preds_text in (" + ', '.join("'" + i + "'" for i in one_year_preds_text) + ")"

    df = pd.read_sql_query(base_query, conn)
    conn.close()
    return [{'label': i, 'value': i} for i in df.fuzzy_water_source.sort_values().unique()]

#clearing
@app.callback(Output('watersource-select', 'value'), [Input('district-select', 'value'), Input('country-select', 'value'), Input('sub-district-select', 'value'), Input('status-select', 'value')])
def update_watersource(district_name, country, sub_district, status_id):
    if district_name is None:
        return None
    if sub_district is None:
        return None

########################################################################################################################################################################
##update water tech
########################################################################################################################################################################
@app.callback(Output('watertech-select', 'options'), [Input('country-select', 'value'), Input('district-select', 'value'),
    Input('sub-district-select', 'value'), Input('status-select', 'value'), Input('watersource-select', 'value'), Input('management-select', 'value'),
    Input('today-pred-select', 'value'), Input('one-year-pred-select', 'value')])
def update_watertech(country,  district, sub_district, status, fuzzy_water_source,  management, today_preds_text, one_year_preds_text):
    conn = psycopg2.connect("dbname='water_db' user='dan' host='postgres-instance2.clhlqrsuvowr.us-east-1.rds.amazonaws.com' password='berkeley'")
    base_query = "SELECT fuzzy_water_tech from menu_table WHERE country_name =" + "'" + str(country) + "'"

    if not sub_district:
        pass
    else:
        base_query = base_query + " and sub_district in (" + ', '.join("'" + i + "'" for i in sub_district) + ")"

    if not district:
        pass
    else:
        base_query = base_query +" and district in (" + ', '.join("'" + i + "'" for i in district) + ")"

    if not status:
        pass
    else:
        base_query = base_query +" and status_id in (" + ', '.join("'" + i + "'" for i in status) + ")"

    if not fuzzy_water_source:
        pass
    else:
        base_query = base_query +" and fuzzy_water_source in (" + ', '.join("'" + i + "'" for i in fuzzy_water_source) + ")"

    if not management:
        pass
    else:
        base_query = base_query +" and management in (" + ', '.join("'" + i + "'" for i in management) + ")"

    if not today_preds_text:
        pass
    else:
        base_query = base_query +" and today_preds_text in (" + ', '.join("'" + i + "'" for i in today_preds_text) + ")"

    if not one_year_preds_text:
        pass
    else:
        base_query = base_query +" and one_year_preds_text in (" + ', '.join("'" + i + "'" for i in one_year_preds_text) + ")"

    df = pd.read_sql_query(base_query, conn)
    conn.close()
    return [{'label': i, 'value': i} for i in df.fuzzy_water_tech.sort_values().unique()]

@app.callback(Output('watertech-select', 'value'), [Input('district-select', 'value'), Input('country-select', 'value'), Input('sub-district-select', 'value'), Input('status-select', 'value'), Input('watersource-select', 'value')])
def update_watertech(district_name, country, sub_district, status_id, fuzzy_water_source):
    if district_name is None:
        return None
    if sub_district is None:
        return None

########################################################################################################################################################################
##update management
########################################################################################################################################################################
@app.callback(Output('management-select', 'options'), [Input('country-select', 'value'), Input('district-select', 'value'),
    Input('sub-district-select', 'value'), Input('status-select', 'value'), Input('watersource-select', 'value'), Input('watertech-select', 'value'),
    Input('today-pred-select', 'value'), Input('one-year-pred-select', 'value')])
def update_management(country,  district, sub_district, status, fuzzy_water_source, fuzzy_water_tech, today_preds_text, one_year_preds_text):
    conn = psycopg2.connect("dbname='water_db' user='dan' host='postgres-instance2.clhlqrsuvowr.us-east-1.rds.amazonaws.com' password='berkeley'")
    base_query = "SELECT management from menu_table WHERE country_name =" + "'" + str(country) + "'"

    if not sub_district:
        pass
    else:
        base_query = base_query + " and sub_district in (" + ', '.join("'" + i + "'" for i in sub_district) + ")"

    if not district:
        pass
    else:
        base_query = base_query +" and district in (" + ', '.join("'" + i + "'" for i in district) + ")"

    if not status:
        pass
    else:
        base_query = base_query +" and status_id in (" + ', '.join("'" + i + "'" for i in status) + ")"

    if not fuzzy_water_source:
        pass
    else:
        base_query = base_query +" and fuzzy_water_source in (" + ', '.join("'" + i + "'" for i in fuzzy_water_source) + ")"

    if not fuzzy_water_tech:
        pass
    else:
        base_query = base_query +" and fuzzy_water_tech in (" + ', '.join("'" + i + "'" for i in fuzzy_water_tech) + ")"

    if not today_preds_text:
        pass
    else:
        base_query = base_query +" and today_preds_text in (" + ', '.join("'" + i + "'" for i in today_preds_text) + ")"

    if not one_year_preds_text:
        pass
    else:
        base_query = base_query +" and one_year_preds_text in (" + ', '.join("'" + i + "'" for i in one_year_preds_text) + ")"

    df = pd.read_sql_query(base_query, conn)
    conn.close()
    return [{'label': i, 'value': i} for i in df.management.sort_values().unique()]

@app.callback(Output('management-select', 'value'), [Input('district-select', 'value'), Input('country-select', 'value'), Input('sub-district-select', 'value'), Input('status-select', 'value'), Input('watersource-select', 'value'), Input('watertech-select', 'value')])
def update_subdistrict(district_name, country, sub_district,  status_id, fuzzy_water_source, fuzzy_water_tech):
    if district_name is None:
        return None
    if sub_district is None:
        return None

########################################################################################################################################################################
##update today_pred menu
########################################################################################################################################################################
@app.callback(Output('today-pred-select', 'options'), [Input('country-select', 'value'), Input('district-select', 'value'),
    Input('sub-district-select', 'value'), Input('status-select', 'value'), Input('watersource-select', 'value'), Input('watertech-select', 'value'),
    Input('management-select', 'value'), Input('one-year-pred-select', 'value')])
def update_today_pre(country,  district, sub_district, status, fuzzy_water_source, fuzzy_water_tech, management,  one_year_preds_text):
    conn = psycopg2.connect("dbname='water_db' user='dan' host='postgres-instance2.clhlqrsuvowr.us-east-1.rds.amazonaws.com' password='berkeley'")
    base_query = "SELECT today_preds_text from menu_table WHERE country_name =" + "'" + str(country) + "'"

    if not sub_district:
        pass
    else:
        base_query = base_query + " and sub_district in (" + ', '.join("'" + i + "'" for i in sub_district) + ")"

    if not district:
        pass
    else:
        base_query = base_query +" and district in (" + ', '.join("'" + i + "'" for i in district) + ")"

    if not status:
        pass
    else:
        base_query = base_query +" and status_id in (" + ', '.join("'" + i + "'" for i in status) + ")"

    if not fuzzy_water_source:
        pass
    else:
        base_query = base_query +" and fuzzy_water_source in (" + ', '.join("'" + i + "'" for i in fuzzy_water_source) + ")"

    if not fuzzy_water_tech:
        pass
    else:
        base_query = base_query +" and fuzzy_water_tech in (" + ', '.join("'" + i + "'" for i in fuzzy_water_tech) + ")"

    if not management:
        pass
    else:
        base_query = base_query +" and management in (" + ', '.join("'" + i + "'" for i in management) + ")"

    if not one_year_preds_text:
        pass
    else:
        base_query = base_query +" and one_year_preds_text in (" + ', '.join("'" + i + "'" for i in one_year_preds_text) + ")"

    df = pd.read_sql_query(base_query, conn)
    conn.close()
    return [{'label': i, 'value': i} for i in df.today_preds_text.sort_values().unique()]

@app.callback(Output('today-pred-select', 'value'), [Input('district-select', 'value'), Input('country-select', 'value'), Input('sub-district-select', 'value'), Input('status-select', 'value'), Input('watersource-select', 'value'), Input('watertech-select', 'value'), Input('management-select', 'value')])
def update_today_pred(district_name, country, sub_district,  status_id, fuzzy_water_source, fuzzy_water_tech, management):
    if sub_district is None:
        return None

########################################################################################################################################################################
##update one year pred menu
########################################################################################################################################################################
@app.callback(Output('one-year-pred-select', 'options'), [Input('country-select', 'value'), Input('district-select', 'value'),
    Input('sub-district-select', 'value'), Input('status-select', 'value'), Input('watersource-select', 'value'), Input('watertech-select', 'value'),
    Input('management-select', 'value'), Input('today-pred-select', 'value')])
def update_year_pred(country,  district, sub_district,status, fuzzy_water_source, fuzzy_water_tech, management, today_preds_text):
    conn = psycopg2.connect("dbname='water_db' user='dan' host='postgres-instance2.clhlqrsuvowr.us-east-1.rds.amazonaws.com' password='berkeley'")
    base_query = "SELECT one_year_preds_text from menu_table WHERE country_name =" + "'" + str(country) + "'"

    if not sub_district:
        pass
    else:
        base_query = base_query + " and sub_district in (" + ', '.join("'" + i + "'" for i in sub_district) + ")"

    if not district:
        pass
    else:
        base_query = base_query +" and district in (" + ', '.join("'" + i + "'" for i in district) + ")"

    if not status:
        pass
    else:
        base_query = base_query +" and status_id in (" + ', '.join("'" + i + "'" for i in status) + ")"

    if not fuzzy_water_source:
        pass
    else:
        base_query = base_query +" and fuzzy_water_source in (" + ', '.join("'" + i + "'" for i in fuzzy_water_source) + ")"

    if not fuzzy_water_tech:
        pass
    else:
        base_query = base_query +" and fuzzy_water_tech in (" + ', '.join("'" + i + "'" for i in fuzzy_water_tech) + ")"

    if not management:
        pass
    else:
        base_query = base_query +" and management in (" + ', '.join("'" + i + "'" for i in management) + ")"

    if not today_preds_text:
        pass
    else:
        base_query = base_query +" and today_preds_text in (" + ', '.join("'" + i + "'" for i in today_preds_text) + ")"

    df = pd.read_sql_query(base_query, conn)
    conn.close()
    return [{'label': i, 'value': i} for i in df.one_year_preds_text.sort_values().unique()]


# @app.callback(Output('one-year-pred-select', 'value'), [Input('district-select', 'value'), Input('country-select', 'value'), Input('sub-district-select', 'value'), Input('status-select', 'value'), Input('watersource-select', 'value'), Input('watertech-select', 'value'), Input('management-select', 'value'), Input('today-pred-select', 'value')])
# def update_one_year_pred(district_name, country, sub_district,  status_id, fuzzy_water_source, fuzzy_water_tech, management, one_year_preds_text):
#     if sub_district is None:
#         return None

if __name__ == '__main__':
    app.run_server(debug=True)