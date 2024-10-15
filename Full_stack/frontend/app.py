import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import numpy as np
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend')))
from data_process import process


df_str, df_male, df_female = process()

new_order_male = [
    'Flyweight', 'Bantamweight', 'Featherweight',
    'Lightweight', 'Welterweight', 'Middleweight',
    'Light Heavyweight', 'Heavyweight'
]

new_order_female = [
    "Women's Strawweight", "Women's Bantamweight",
    "Women's Featherweight", "Women's Flyweight"
]

def create_heatmap(df, order):
    df['weight_class'] = pd.Categorical(df['weight_class'], categories=order, ordered=True)
    df_sorted = df.sort_values('weight_class')
    heatmap_data = df_sorted.set_index('weight_class')['avg_SIG_STR_pct']

    fig = px.imshow(
        heatmap_data.values.reshape(-1, 1),
        labels=dict(x='Significant Strike Percentage', y='Weight Class'),
        x=[heatmap_data.name],
        y=heatmap_data.index,
        color_continuous_scale='Greens'
    )
    fig.update_layout(title="Significant Strike Percentage by Weight Class")
    return fig

def create_line_plot(df):
    df_melted = df.melt(id_vars='Age', value_vars=['FEMALE', 'MALE'])
    fig = px.line(df_melted, x='Age', y='value', color='gender',
                  title='Average SIG STR Landed by Age and Gender',
                  labels={'value': 'Average SIG STR Landed', 'Age': 'Age'},
                  line_shape='linear')
    fig.update_traces(mode='lines+markers')
    return fig

heatmap_male = create_heatmap(df_male, new_order_male)
heatmap_female = create_heatmap(df_female, new_order_female)
line_plot = create_line_plot(df_str)

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Graph(figure=heatmap_male, id='heatmap-male'),
    dcc.Graph(figure=heatmap_female, id='heatmap-female'),
    dcc.Graph(figure=line_plot, id='line-plot')
])

if __name__ == '__main__':
    app.run_server(debug=True)
