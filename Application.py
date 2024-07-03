from dash import Dash, dcc, html, Output, Input
import plotly.express as px
import pandas as pd



app = Dash(__name__)
server = app.server
#df = pd.read_csv('https://gist.githubusercontent.com/chriddyp/5d1ea79569ed194d432e56108a04d188/raw/a9f9e8076b837d541398e999dcbac2b2826a81f8/gdp-life-exp-2007.csv')
df = pd.read_csv('file:///C:/Users/Shahidul%20Saad/Desktop/m1.5.txt')
# Iterate through each column
for col in df.columns:
    Data =df[col].str.split(';', expand=True)
# All the 28 Strings voltages
for col in df.columns:
    Strings = ((Data.iloc[:, 30:57].astype(float))+200)/100
# All 6 temp probe and the max, min temp 
for col in df.columns:
    Temperatures = Data.iloc[:, 63:68].astype(float)
Pack_Volatge =(Data.iloc[:, 29].astype('float64'))/10.0
data_position = [19, 69,62]


# Now let's work on the layout itself
app.layout = html.Div(style= {'backgroundColor':'#121212', 'textAlign': 'center'}, children= [html.H1('Hello Evoke'),
             html.Div(style= {'textAlign': 'center','backgroundColor': '#121212'}, children = 'This is a simple example of plotting the voltage of the vehicle'),
             html.Div(id='slider-output', style={'fontSize': 60}),
             dcc.Slider(1, 100, 1, value=5, id='slider'),
             dcc.Graph(id="voltage")])

@app.callback(
    Output(component_id='slider-output', component_property='children'),
    #Output(component_id='voltage', component_property='figure'),
    Input(component_id='slider', component_property='value'),
)
def updata_figure(number):
    #filtered_df = Data[number]
   # fig = px.line(filtered_df,  y=filtered_df, title='Test of Dash')
    return  number * number
# let's run the app
if __name__ == '__main__':
    app.run_server(debug=True)

