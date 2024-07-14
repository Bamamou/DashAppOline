import dash
from dash import html, dcc, Input, Output, State
import pandas as pd
import numpy as np
import base64
import io
import plotly.express as px
import dash_bootstrap_components as dbc

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG, dbc.icons.FONT_AWESOME, dbc.icons.BOOTSTRAP])
app.title ="EvokeOBD"

colors = {
    'background': '#202020',
    'papercolor': '#202020',
    'text': '#7FDBFF'
}

# Define the app layout
app.layout = html.Div([
    html.H1("Evoke Motorcycles OBD vizualizer", style={'textAlign': 'center','font-weight': 'bold', 'color': colors["text"], "font-family":'Courier New'}, className="bg-primary text-white text-center p-3 h3 mb-2 "),
    html.Div(children='This web based App helps backend engineers troubleshoot errors and analyse vehicle performance based on OBD data.', style={'textAlign': 'center',  'color': colors['text'], "font-family":'Courier New', "font-size": "18px"}),
    dcc.Upload(
        id="upload-data",
        children=dbc.Button([html.I(className="fa-solid fa-cloud-arrow-down me-2"), "Upload"], color = "primary", className ="me-2"),
        multiple=False
    ),
    dcc.Checklist(
            options=[" Urban", " M1.5"],
            id="toppings"), 
   
    html.Div(id="output-data-upload"),
    dcc.Dropdown(id="column-dropdown", style={"width": "50%", "margin": "10px auto"," font-size": "16px"}, multi=True,searchable=True),  # Allow multiple selections
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
        for col in df.iloc[:, 62:68]:
            df.rename(columns={col:'Temperature'+str(col-62)}, inplace = True)
        # divide the below values by 10
        df[29] =df[29].div(10)   # BMS pack voltgae 
        df[81] =df[81].div(10)   #MCU pack voltage
        df[10] =df[10].div(10)   #ECU supply voltage
        df.rename(columns = {1:'packetCode', 2:'second', 3:'minute', 4: 'hour', 5:'dayW', 6:'dayM',  7:'month',  8:'year', 9:'boardTemperature', 
                        10:'boardSupplyVoltage', 11:'odometerKm', 12:'tripKm', 13:'speedKmh',  14:'maximumSpeed', 15:'rpm', 16:'efficiency', 17:'vehicleStatuByte1', 18:'vehicleStatuByte2', 19:'numActiveErrors', 
                        20:'sumActiveErrors', 21:'roll', 22:'pitch', 23:'frontTirePressure', 24:'frontTireTemperature', 25:'rearTirePressure', 26:'rearTireTemperature', 27:'inputsI2C', 28:'outputsI2C', 29:'Pack Voltage',  
                        62:'Pack_DSG_Current', 69:'SOC', 
                        70:'BatteryPhysicalCapacity', 71:'BatteryRemainingCapacity', 72:'BMSTurnOnTime', 73:'CellHighestVoltageNumber', 74:'CellHighestVoltageValue', 75:'CellLowestVoltageNumber', 76:'CellLowestVoltageValue', 77:'NumberOfBatteries', 78:'ChargingMosfetStatus', 79:'DischargingMosfetStatus', 
                        80:'BalanceStateSign', 81:'MCU_Voltage', 82:'MCUBus_Current', 83:'RPM', 84:'Motor_Temp', 85:'Invt_Temp', 89:'MCU_state', 
                        90:'Throttle', 91:'LowByteError', 92:'HighByteError', 93:'StatusByte', 94:'MCUOutCurrent', 95:'MCUMaxRegen', 96:'maximumThrottle', 97:'minimumThrottle', 98:'chargerVoltage', 99:'chargerCurrent', 
                        100:'chargerStatusByte', 101:'maxChargerVoltage', 102:'Fan_Speed', 103:'millis', 104:'resetReason'}, inplace = True)

        # df.rename(columns = {29:'Pack Voltage', 9:'boardTemperature', 10:'boardSupplyVoltage', 11:'odometerKm', 12:'tripKm', 13:'speedKmh',
        #                14:'maximumSpeed',  16: 'efficiency', 17:'vehicleStatuByte1', 18:'vehicleStatuByte2', 69:'SOC', 62:'Pack_DSG_Current',
        #                85:'Invt_Temp', 83:'RPM', 81:'MCU_Voltage', 84:'Motor_Temp'}, inplace = True)

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
        for col in df.iloc[:, 62:68]:
            df.rename(columns={col:'Temperature'+str(col-62)}, inplace = True)
        #Divide the pack voltage per 10   
        df[29] =df[29].div(10)   # BMS pack voltgae 
        df[81] =df[81].div(10)   #MCU pack voltage
        df[10] =df[10].div(10)   #ECU supply voltage
        #Rename some columns
        df.rename(columns = {1:'packetCode', 2:'second', 3:'minute', 4: 'hour', 5:'dayW', 6:'dayM',  7:'month',  8:'year', 9:'boardTemperature', 
                        10:'boardSupplyVoltage', 11:'odometerKm', 12:'tripKm', 13:'speedKmh',  14:'maximumSpeed', 15:'rpm', 16:'efficiency', 17:'vehicleStatuByte1', 18:'vehicleStatuByte2', 19:'numActiveErrors', 
                        20:'sumActiveErrors', 21:'roll', 22:'pitch', 23:'frontTirePressure', 24:'frontTireTemperature', 25:'rearTirePressure', 26:'rearTireTemperature', 27:'inputsI2C', 28:'outputsI2C', 29:'Pack Voltage',  
                        62:'Pack_DSG_Current', 69:'SOC', 
                        70:'BatteryPhysicalCapacity', 71:'BatteryRemainingCapacity', 72:'BMSTurnOnTime', 73:'CellHighestVoltageNumber', 74:'CellHighestVoltageValue', 75:'CellLowestVoltageNumber', 76:'CellLowestVoltageValue', 77:'NumberOfBatteries', 78:'ChargingMosfetStatus', 79:'DischargingMosfetStatus', 
                        80:'BalanceStateSign', 81:'MCU_Voltage', 82:'MCUBus_Current', 83:'RPM', 84:'Motor_Temp', 85:'Invt_Temp', 89:'MCU_state', 
                        90:'Throttle', 91:'LowByteError', 92:'HighByteError', 93:'StatusByte', 94:'MCUOutCurrent', 95:'MCUMaxRegen', 96:'maximumThrottle', 97:'minimumThrottle', 98:'chargerVoltage', 99:'chargerCurrent', 
                        100:'chargerStatusByte', 101:'maxChargerVoltage', 102:'Fan_Speed', 103:'millis', 104:'resetReason'}, inplace = True)

        # df.rename(columns = {29:'Pack Voltage', 9:'boardTemperature', 10:'boardSupplyVoltage', 11:'odometerKm', 12:'tripKm', 13:'speedKmh',
        #                14:'maximumSpeed',  16: 'efficiency', 17:'vehicleStatuByte1', 18:'vehicleStatuByte2', 69:'SOC', 62:'Pack_DSG_Current',
        #                85:'Invt_Temp', 83:'RPM', 81:'MCU_Voltage', 84:'Motor_Temp'}, inplace = True)

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
    app.run_server(debug=True)
