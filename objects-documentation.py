# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()


# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                  options=[{'label': 'All Sites', 'value': 'ALL'},
                                  {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                  {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                  {'label': 'KSC LC-39A', 'value':'KSC LC-39A' },
                                  {'label': 'CAFS SLC-40', 'value': 'CAFS SLC-40'}
                                  ],
                                  value="ALL",
                                  placeholder="Select a Launch Site here",
                                  searchable=True
                                ),
                                html.Br(),

                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                    min=0, max=10000, step=1000,
                                    marks={0: '0',
                                        2500: '2500',
                                        5000: "5000",
                                        7500: "7500",
                                        10000: "10000"
                                        },
                                    value=[min_payload, max_payload]),

                                # Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df[["Launch Site", "class"]]
    if entered_site == 'ALL':
        data = pd.DataFrame(filtered_df.groupby("Launch Site").count())
        fig = px.pie(data, values='class', 
        names=["CCAFS LC-40", "VAFB SLC-4E", "KSC LC-39A", "CAFS SLC-40"], 
        title='Total Success Launches By Site')
        return fig
    else:
        data = pd.DataFrame(filtered_df[filtered_df["Launch Site"]== entered_site].groupby("class").count())
        data.columns = ["Count"]
        fig = px.pie(data, values='Count', 
        names=["class=0", "class=1"], 
        title='Total Success Launches For Site '+entered_site)
        return fig




# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'), 
              Input(component_id="payload-slider", component_property="value")])
def get_scatter_plot(entered_site, range):
    if entered_site == 'ALL':
        fig = px.scatter(spacex_df, x='Payload Mass (kg)', y='class', 
        color="Booster Version Category",
        title='Correlation between Payload and Success for all Sites')
        return fig
    else:
        filtered_df = spacex_df[spacex_df["Launch Site"] == entered_site]
        print(filtered_df)
        fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', 
        color="Booster Version Category",
        title='Correlation between Payload and Success for '+entered_site)
        return fig



# Run the app
if __name__ == '__main__':
    app.run_server()
