from dash import Dash, dcc, html
import plotly.express as px
import pandas as pd



app = Dash(__name__)
server = app.server
#df = pd.read_csv('https://gist.githubusercontent.com/chriddyp/5d1ea79569ed194d432e56108a04d188/raw/a9f9e8076b837d541398e999dcbac2b2826a81f8/gdp-life-exp-2007.csv')
df = pd.read_csv('C:\\Users\\admin\\Documents\\GitHub\\Pyhton_Jupiter\\Data\\Battery\\Balistron1.txt',  header=None, na_values=[''], skipinitialspace=True)
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

fig =px.line( y=Pack_Volatge)

#Now let's set the layout colors of our app
fig.update_layout(
    plot_bgcolor ='#121212',    # The bg of the plot
    paper_bgcolor = '#121212',  # The bg of the paper 
    font_color = '#1876AE'      # The text on the plot (Inside the plot only)
)
# Now let's work on the layout itself
app.layout = html.Div(style= {'backgroundColor':'#121212', 'textAlign': 'center'}, children= [html.H1('Hello Evoke'),
             html.Div(style= {'textAlign': 'center','backgroundColor': '#121212'}, children = 'This is a simple example of plotting the voltage of the vehicle'),

             dcc.Graph(id="life-exp-vsgdp", figure = fig)])


# let's run the app
if __name__ == '__main__':
    app.run_server(debug=False)