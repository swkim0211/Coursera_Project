# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
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
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=[{'label': 'All Sites', 'value': 'ALL'}] + [
                                        {'label':s, 'value':s} for s in sorted(spacex_df['Launch Site'].unique())
                                    ],
                                    value='ALL',
                                    placeholder='Select a Launch Site',
                                    searchable=True
                                    ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0,
                                    max=10000,
                                    step=1000,
                                    value=[min_payload, max_payload],
                                    marks={0: '0', 2500: '2.5k', 5000: '5k', 7500: '7.5k', 10000: '10k'}
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        df_all = (spacex_df.groupby('Launch Site', as_index=False)['class'].sum())
        fig = px.pie(
            df_all,
            values='class',
            names='Launch Site',
            title='Total Successful Launches by Site'
        )
    else:
        dff = spacex_df[spacex_df['Launch Site'] == entered_site]
        counts = (dff['class'].value_counts()
                        .rename_axis('Outcome')
                        .reset_index(name='count'))
        counts['Outcome'] = counts['Outcome'].map({1: 'Success', 0: 'Failure'})
        fig = px.pie(
            counts,
            values='count',
            names='Outcome',
            title=f'Success vs Failure at {entered_site}'
        )
    return fig
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [
        Input('site-dropdown', 'value'),
        Input('payload-slider', 'value')
    ]
)
def update_scatter(selected_site, payload_range):
    low, high = payload_range
    dff = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]

    fig = px.scatter(
        dff,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        hover_data=['Launch Site', 'Booster Version Category'],
        title=('Payload vs. Outcome (All Sites)'
               if selected_site == 'ALL'
               else f'Payload vs. Outcome — {selected_site}')
    )

    fig.update_yaxes(title='Class (0=Fail, 1=Success)', tickmode='array', tickvals=[0, 1])
    fig.update_xaxes(title='Payload Mass (kg)')
    fig.update_layout(legend_title_text='Booster Version')

    return fig

# Run the app
if __name__ == '__main__':
    app.run()
