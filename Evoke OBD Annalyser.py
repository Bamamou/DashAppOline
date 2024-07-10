import dash
from dash import html, dcc, Input, Output, State
import pandas as pd
import numpy as np
import base64
import io
import plotly.express as px
import dash_bootstrap_components as dbc

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME, dbc.icons.BOOTSTRAP])
app.title ="EvokeOBD"

colors = {
    'background': '#202020',
    'papercolor': '#202020',
    'text': '#7FDBFF'
}

# Define the app layout
app.layout = html.Div([
    html.H1("Evoke Motorcycles OBD vizualizer", style={'textAlign': 'center', 'color': colors["text"]}),
    html.Div(children='This web based App helps backend engineers troubleshoot errors and analyse vehicle performase based on OBD data.', style={'textAlign': 'center',  'color': colors['text']}),
    dcc.Upload(
        id="upload-data",
        children=dbc.Button([html.I(className="fa-solid fa-cloud-arrow-down me-2"), "Upload"], color = "primary", className ="me-2"),
        multiple=False
    ),
    html.Div(id="output-data-upload"),
    dcc.Dropdown(id="column-dropdown", multi=True),  # Allow multiple selections
    dcc.Graph(id="plot")
])

# Define callback to handle file upload
@app.callback(
    [Output("output-data-upload", "children"),
     Output("column-dropdown", "options")],
    [Input("upload-data", "contents")],
    [State("upload-data", "filename")]
)
def upload_file(contents, filename):
    if contents is None:
        return "Please upload a file.", []
    else:
        # Read the uploaded file
        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        for col in df.columns:
            df =df[col].str.split(';', expand=True)
                # Remove the first colunm which has time and date
            df =df.iloc[:, 1:]
        def to_float(x):
            return float(x) if x != '' else np.nan
            # Apply the conversion function to the entire DataFrame
        df = df.map(to_float)
        # Let's compute the voltage of each Cell an convert it to V
        for col in df.iloc[:, 29:56]:
            df[col] =(df[col]+200)/100
            df.rename(columns={col:'String'+str(col-29)}, inplace = True)
        # Let's also rename the temperature columns
        for col in df.iloc[:, 62:67]:
            df.rename(columns={col:'Temperature'+str(col-62)}, inplace = True)
        # divide the below values by 10
        df[29] =df[29].div(10)   # BMS pack voltgae 
        df[81] =df[81].div(10)   #MCU pack voltage
        df[10] =df[10].div(10)   #ECU supply voltage
        df.rename(columns = {29:'Pack Voltage', 9:'boardTemperature', 10:'boardSupplyVoltage', 11:'odometerKm', 12:'tripKm', 13:'speedKmh',
                       14:'maximumSpeed',  16: 'efficiency', 17:'vehicleStatuByte1', 18:'vehicleStatuByte2', 69:'SOC', 62:'Pack_DSG_Current',
                       85:'Invt_Temp', 83:'RPM', 81:'MCU_Voltage', 84:'Motor_Temp'}, inplace = True)

        # Create dropdown options from column names
        column_options = [{"label": col, "value": col} for col in df.columns]

        return f"File {filename} uploaded successfully.", column_options

# Define callback to handle plot
@app.callback(
    Output("plot", "figure"),
    [Input("column-dropdown", "value")],
    [State("upload-data", "contents")]
)
def plot_selected_columns(selected_columns, contents):
    if selected_columns and contents:
        # Read the uploaded file
        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode("utf-8")))
        for col in df.columns:
            df =df[col].str.split(';', expand=True)
                # Remove the first colunm which has time and date
            df =df.iloc[:, 1:]
        def to_float(x):
            return float(x) if x != '' else np.nan
            # Apply the conversion function to the entire DataFrame
        df = df.map(to_float)
        # Let's compute the voltage of each Cell an convert it to V
        for col in df.iloc[:, 29:56]:
            df[col] =(df[col]+200)/100
            df.rename(columns={col:'String'+str(col-29)}, inplace = True)
        # Let's also rename the temperature columns
        for col in df.iloc[:, 62:67]:
            df.rename(columns={col:'Temperature'+str(col-62)}, inplace = True)
        #Divide the pack voltage per 10   
        df[29] =df[29].div(10)   # BMS pack voltgae 
        df[81] =df[81].div(10)   #MCU pack voltage
        df[10] =df[10].div(10)   #ECU supply voltage
        #Rename some columns
        df.rename(columns = {29:'Pack Voltage', 9:'boardTemperature', 10:'boardSupplyVoltage', 11:'odometerKm', 12:'tripKm', 13:'speedKmh',
                       14:'maximumSpeed',  16: 'efficiency', 17:'vehicleStatuByte1', 18:'vehicleStatuByte2', 69:'SOC', 62:'Pack_DSG_Current',
                       85:'Invt_Temp', 83:'RPM', 81:'MCU_Voltage', 84:'Motor_Temp'}, inplace = True)

        # Plot the selected columns
        fig = px.line(df, x=df.index, y=selected_columns, title="Plot of Selected Data")
        # Let's give some color to our plot
        fig.update_layout(
        plot_bgcolor ='#121212',    # The bg of the plot
        paper_bgcolor = '#121212',  # The bg of the paper 
        font_color = '#1876AE'      # The text on the plot (Inside the plot only)
        )
        return fig
    
    else:
        return {}

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True, port=8888)
