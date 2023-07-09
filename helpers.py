import sqlite3
import io
import urllib
import base64
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import matplotlib.ticker as ticker
import numpy as np

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_vote_data(bundestags_id, abstimmungsverhalten):
    conn = get_db_connection()
    query = f"WITH abs AS (SELECT * FROM df_abstimmungen_selenium WHERE bundestags_id = {bundestags_id}), pol AS (SELECT * FROM df_politiker_selenium WHERE bundestags_id = {bundestags_id}), alldata AS (SELECT * FROM abs LEFT JOIN pol ON abs.bundestags_id = pol.bundestags_id) SELECT DISTINCT * FROM alldata WHERE Abstimmungsverhalten = '{abstimmungsverhalten}'"
    data = conn.execute(query).fetchall()
    conn.close()
    return data

def twitter_nutzung_chart1(df):
    df['date'] = pd.to_datetime(df['date'])
    df['partei'] = df['partei'].str.replace('Bundestagsfraktion', '')
    df['partei'] = df['partei'].str.replace('-', '')

    # Set the date column as the index of the DataFrame
    df.set_index('date', inplace=True)

    # Group the data by month and party and count the number of tweets
    grouped = df.groupby([pd.Grouper(freq='Q'), 'partei'])['count(*)'].size()

    def date_to_quarter(date):
        date = pd.to_datetime(date, format='%Y-%m-%d')
        quarter_end = date + pd.offsets.QuarterEnd()
        return 'Q{} {}'.format((quarter_end.month-1)//3 + 1, quarter_end.year)

    # Define a color map that maps each party to a color
    colors = {' Bündnis 90/Die Grünen': '#1AA037',
              'CDU/CSU': 'black',
              ' Die Linke.': '#A6006B',
              'FDP': '#FFEF00',
              'SPD': '#E3000F',
               'fraktionslos': '#0080FF',
             'AfD': '#0489DB'}

    # Reshape the data and plot the stacked bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    grouped.unstack().plot(kind='bar', stacked=True, ax=ax, color=[colors.get(c, 'gray') for c in grouped.unstack().columns])

    # get the current tick labels
    labels = ax.get_xticklabels()

    # apply the function to the labels
    new_labels = [date_to_quarter(label.get_text()) for label in labels]

    # set the new tick labels
    ax.set_xticklabels(new_labels, fontsize=15)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(4))

    # Set the axis labels and title
    fig.suptitle('Montaliche Tweets je derzeitiger Bundestagsfraktion', fontsize=15, fontweight='bold', fontfamily='Arial')

    ax.set_xlabel('Jahresviertel', fontsize=15)
    ax.set_ylabel('')
    ax.set_title('Grafik zeigt Tweets aller derzeitigen Parliamentarier groupiert in Fraktionen', fontstyle='italic', fontfamily='Arial', fontsize=10)

    # do additional visualization stuff
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['left'].set_visible(False)
    plt.gca().spines['bottom'].set_visible(False)

    ## background color
    fig = plt.gcf()
    ax.set_facecolor('#b1d1fc')
    fig.set_facecolor('#b1d1fc')

    ## watermark
    ax.text(0.95, 0.05, '@Politix', alpha=0.5, ha='center', va='center', transform=ax.transAxes, fontsize=10)

    # Move the legend outside of the plot area
    ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left', facecolor='#FFFFFF')


    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight', pad_inches=0.1)
    img.seek(0)
    plot_data = urllib.parse.quote(base64.b64encode(img.read()).decode())

    return plot_data

def get_politician_info(bundestags_id):
    conn = get_db_connection()
    query = f"WITH abs AS (SELECT * FROM df_abstimmungen_selenium WHERE bundestags_id = {bundestags_id}), pol AS (SELECT * FROM df_politiker_selenium WHERE bundestags_id = {bundestags_id}) SELECT * FROM abs LEFT JOIN pol ON abs.bundestags_id = pol.bundestags_id"
    data = conn.execute(query).fetchall()
    return data


def generate_pie_chart(df):
    df = df.groupby('Abstimmungsverhalten').size().reset_index(name='count')
    colors = ['#ffc107', '#28a745', '#dc3545', '#6c757d']
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(aspect="equal"))
    ax.pie(df['count'], labels=df['Abstimmungsverhalten'], autopct='%1.1f%%', startangle=90, wedgeprops={'linewidth': 3, 'edgecolor': 'k', 'antialiased': True}, textprops={'fontsize': 18}, colors=colors)

    fig.set_facecolor('#ffc107')
    ax.set_title('Abstimmungsverhalten', fontsize=24, fontweight='bold')

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_data = urllib.parse.quote(base64.b64encode(img.read()).decode())

    return plot_data

    