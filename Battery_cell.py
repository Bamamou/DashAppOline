# Install the required libraries if not already installed
# !pip install dash pandas dash-bootstrap-components

import dash
from dash import html, dcc, Input, Output, State
import pandas as pd
import io
import base64
import plotly.express as px
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
from plotly.subplots import make_subplots
import numpy as np
import dash_daq as daq

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title ="EvokeOBD"
colors = {
    'background': '#202020',
    'papercolor': '#202020',
    'text': '#7FDBFF'
}
picker_style = {'float': 'left', 'margin': 'auto'}
drop_down_icon = html.I(className="bi bi-chevron-double-down me-2")
# Define the app layout
app.layout = html.Div([
    html.H1("Evoke Battery Cell Data Analyser", style={'textAlign': 'center', 'color': colors["text"]}, className="bg-primary text-white text-center p-3 h3 mb-2 "),
    dcc.Upload(
        id="upload-data",
        children=html.Div([
            "Drag and drop or click to select an OBD file"
        ]),
        style={
            "width": "50%",
            "height": "60px",
            "lineHeight": "60px",
            "borderWidth": "1px",
            "borderStyle": "dashed",
            "borderRadius": "5px",
            "textAlign": "center",
            "margin": "10px auto",
        },
        multiple=False
    ),
    dcc.Dropdown(
        id="column-dropdown",
        options=[],
        placeholder="Select a data",
        #drop_down_icon,  
       # color = "primary", className ="me-2",
        maxHeight=300,
        #multi=True,
        style={"width": "50%", "margin": "10px auto"," font-size": "16px"},
        clearable=True,
        searchable=True
    ),
    dcc.Graph(id="data-plot"),
    # Not critcal and can be remove the color picker is not needed
    dcc.Dropdown(
        id='dropdown',
        multi=True,
        style={"width": "50%", "margin": "10px auto"," font-size": "16px"},
        searchable=True
        ),
        
    dcc.Graph(id='subplot'),
    daq.ColorPicker(
        id='font', label='Font Color', size=150,
        style=picker_style, value=dict(hex='#1876AE')),
    daq.ColorPicker(
        id='title', label='Title Color', size=150,
        style=picker_style, value=dict(hex='#1876AE')),
])

# Define callback to handle file upload
@app.callback(
    Output("column-dropdown", "options"),
    Output("dropdown", "options"),
    Output("column-dropdown", "value"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),

)


def update_uploaded_file(contents, filename):
    if contents is None:
        return [], [], None

  # Read the uploaded CSV file
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    df = pd.read_csv(io.StringIO(decoded.decode("gbk")))

    df.dropna( 
            how='all',
            axis=0,
            inplace= True)
    # Let's remove the time section of the data frame since it is not needed.
    df = df.iloc[:, 1:]
    # Let's create an array to hold the index of each change in the mode
    change_indexes = []
    # These are the columns in the dataframe.
    voltage_mV  = df["电压(mV)"]
    current_mA  = df["电流(mA)"]
    capacity_Ah = df["容量(mAH)"]
    energy_Ah   = df["电量(mWH)"]
    mode        = df["模式"]
    Voltage_cycle  = []
    current_cycle = []
    #Check for changes in the 'mode' column
    for i in range(1, len(df)):
        if df["模式"].iloc[i] != df["模式"].iloc[i - 1]:
            change_indexes.append(i)
    for i in range(len(change_indexes) - 1):
        Voltage_cycle.append(voltage_mV[change_indexes[i]:change_indexes[i+1]])
        current_cycle.append(current_mA[change_indexes[i]:current_mA[i+1]])

    # Get column names for dropdown options
    column_options = [{"label": col, "value": col} for col in df.columns]
    column_option = [{"label": col, "value": col} for col in df.columns]

    return column_options, column_option, column_options[0]["value"]

# Define callback to filter data based on selected column
@app.callback(
    Output("data-plot", "figure"),
    Input("column-dropdown", "value"),
    State("upload-data", "contents"),
    # Can be removed if the color picker is not needed
    Input("font", 'value'),
    Input("title", 'value')
)
def update_plot(selected_column, contents, font_color, title_color):
    if contents is None:
        return {}

# Read the uploaded CSV file
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    df = pd.read_csv(io.StringIO(decoded.decode("gbk")))

    df.dropna( 
            how='all',
            axis=0,
            inplace= True)
    # Let's remove the time section of the data frame since it is not needed.
    df = df.iloc[:, 1:]
    # Let's create an array to hold the index of each change in the mode
    change_indexes = []
    # These are the columns in the dataframe.
    voltage_mV  = df["电压(mV)"]
    current_mA  = df["电流(mA)"]
    capacity_Ah = df["容量(mAH)"]
    energy_Ah   = df["电量(mWH)"]
    mode        = df["模式"]
    #Check for changes in the 'mode' column
    for i in range(1, len(df)):
        if df["模式"].iloc[i] != df["模式"].iloc[i - 1]:
            change_indexes.append(i)

    
    # Create a scatter plot
   # fig =  px.line(df, x="selected_column", y=selected_column)
    fig = px.line(df, x=df.index, y=selected_column, title= f"Plot of {selected_column} over time")
     # Let's give some color to our plot
    fig.update_layout(
    plot_bgcolor ='#121212',    # The bg of the plot
    paper_bgcolor = '#121212',  # The bg of the paper 
    font_color=font_color['hex'],
    title_font_color=title_color['hex'],
   # font_color = '#1876AE',      # The text on the plot (Inside the plot only)
    font_family="Times new roman", # font 
    font_size = 18
    )
   
        
       
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False)

    return fig


    
# ============================ Section of the subplots =============================

# Callback to update the subplot
@app.callback(
Output('subplot', 'figure'),
[Input("dropdown", "value")],
[State("upload-data", "contents")]
)
def update_subplot(selected_column, contents):
  
    if selected_column and contents:
        # Read the uploaded file
        # Read the uploaded CSV file
        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode("gbk")))

        df.dropna( 
                how='all',
                axis=0,
                inplace= True)
        # Let's remove the time section of the data frame since it is not needed.
        df = df.iloc[:, 1:]
        # Let's create an array to hold the index of each change in the mode
        change_indexes = []
        # These are the columns in the dataframe.
        voltage_mV  = df["电压(mV)"]
        current_mA  = df["电流(mA)"]
        capacity_Ah = df["容量(mAH)"]
        energy_Ah   = df["电量(mWH)"]
        mode        = df["模式"]
        #Check for changes in the 'mode' column
        for i in range(1, len(df)):
            if df["模式"].iloc[i] != df["模式"].iloc[i - 1]:
                change_indexes.append(i)

        subplots = make_subplots(rows=4, cols=1, shared_xaxes=True, subplot_titles=selected_column, print_grid=False, horizontal_spacing=0.015,)

        for i, col in enumerate(selected_column[:4]):
            subplots.add_trace(go.Scatter(x=df.index, y=df[col], mode='lines', name=col),
                row=i+1, col=1
        )
    # Add empty subplots if fewer than 3 columns are selected
 # Add empty subplots if fewer than 3 columns are selected
        for i in range(len(selected_column), 1):
            subplots.add_trace(go.Scatter(x=[], y=[]), row=i+1, col=1)
            #subplots.update_layout( title_text="Subplot of Selected Columns", plot_bgcolor ='#121212',   paper_bgcolor = '#121212',  font_color = '#1876AE'  )
            subplots.update_layout(
                print_grid=False,
                height=1500,
                width=600,
                autosize=False,
                plot_bgcolor ='#121212',    # The bg of the plot
                paper_bgcolor = '#121212',  # The bg of the paper 
                # font_color=font_color['hex'],
                # title_font_color=title_color['hex'],
            # font_color = '#1876AE',      # The text on the plot (Inside the plot only)
                font_family="Times new roman", # font 
                font_size = 18 )
    
        return subplots
    else:
        return {}


if __name__ == "__main__":
    app.run_server(debug=True)
