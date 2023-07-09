from flask import Flask, request, render_template, url_for, send_file
import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from helpers import get_db_connection, get_vote_data, generate_pie_chart, get_politician_info, twitter_nutzung_chart1


app = Flask(__name__)

# Routes

@app.route("/")
def home():
    conn = get_db_connection()
    data = conn.execute("SELECT * FROM df_politiker_selenium ORDER BY RANDOM() Limit 3").fetchall()
    politicians = []
    for row in data:
        politician = {}
        politician['vorname'] = row[1]
        politician['nachname'] = row[2]
        politician['bundestags_id'] = row[0]
        politician['beruf'] = row[10]
        politician['bundesland'] = row[11]
        politician['wahlkreis_id'] = row[12]
        politician['partei'] = row[9]
        politician['img_url'] = row[8]
        politicians.append(politician)
    return render_template('home.html', politicians=politicians)


    
@app.route("/politiker")
def politiker():
    name_filter = request.args.get('name')
    sort_by = request.args.get('sort')
    conn = get_db_connection()

    #Filter
    if not name_filter:
        data = conn.execute(f"SELECT * FROM df_politiker_selenium").fetchall()
    else:
        data = conn.execute(f"SELECT * FROM df_politiker_selenium WHERE vorname LIKE '%{name_filter}%'").fetchall()
    
    #Sorting
    if sort_by == 'name':
        data.sort(key=lambda row: row['vorname'] + row['nachname'])
    elif sort_by == 'party':
        data.sort(key=lambda row: row['partei'])
    elif sort_by == 'constituency':
        data.sort(key=lambda row: row['wahlkreis_id'])

    conn.close()
    return render_template('politiker.html', data=data)

@app.route("/abstimmungen")
def abstimmungen():
    name_filter = request.args.get('name')
    conn = get_db_connection()

    if not name_filter:
        data = conn.execute(f"SELECT DISTINCT Abstimmungsthema FROM df_abstimmungen_selenium").fetchall()
    else:
        data = conn.execute(f"SELECT DISTINCT Abstimmungsthema FROM df_abstimmungen_selenium WHERE Abstimmungsthema LIKE '%{name_filter}%'").fetchall()
        
    conn.close()
    return render_template('abstimmungen.html', data=data)

@app.route("/parteien")
def parteien():
    conn = get_db_connection()
    query = f"SELECT DISTINCT partei FROM df_politiker_selenium"
    df = pd.read_sql_query(query, conn)
    parteien = df['partei'].tolist()
    return render_template('parteien.html', parteien=parteien)
                           
@app.route('/parteien_profile', methods=['POST'])
def parteien_profile():
    partei_name = request.form['partei']
    conn = get_db_connection()

    # data body
    query = f"SELECT * FROM df_politiker_selenium WHERE partei LIKE '%{partei_name}%'"
    data = conn.execute(query).fetchall()
    
    df = pd.read_sql_query(query, conn)
    partei = data[0][9]

    return render_template('parteien_profile.html', partei=partei)

@app.route("/abstimmungsverhalten", methods=['POST'])
def abstimmungsverhalten():
    bundestags_id = request.form['bundestags_id']
    conn = get_db_connection()

    # data body
    query = f"WITH abs AS (SELECT * FROM df_abstimmungen_selenium WHERE bundestags_id = {bundestags_id}), pol AS (SELECT * FROM df_politiker_selenium WHERE bundestags_id = {bundestags_id}) SELECT * FROM abs LEFT JOIN pol ON abs.bundestags_id = pol.bundestags_id"
    data = conn.execute(query).fetchall()
    
    df = pd.read_sql_query(query, conn)

    # data profile
    data2 = conn.execute(f"SELECT * FROM df_politiker_selenium WHERE bundestags_id = {bundestags_id}").fetchone()
    vorname = data2[1]
    nachname = data2[2]
    bundestags_id = data2[0]
    beruf = data2[10]
    bundesland = data2[11]
    wahlkreis_id = data2[12]
    partei = data2[9]
    img_url = data2[8]
    website_links = data2[6]
    facebook_links = data2[4]
    twitter_links = data2[5]
    instagram_links = data2[7]
 
    # data votes
    data3 = get_vote_data(bundestags_id, 'Nein')
    data4 = get_vote_data(bundestags_id, 'Ja')
    data5 = get_vote_data(bundestags_id, 'Enthalten')
    data6 = get_vote_data(bundestags_id, 'Nicht abg.')


    # creating the visuals
    plot_data = generate_pie_chart(df)
    

    # closing db
    conn.close()
    
    return render_template('abstimmungsverhalten.html', data=data, data3=data3, data4=data4, data5=data5, data6=data6, plot_url=plot_data, vorname=vorname, nachname=nachname, bundestags_id=bundestags_id, beruf=beruf, bundesland=bundesland, partei=partei, img_url=img_url, wahlkreis_id=wahlkreis_id, website_links=website_links, facebook_links=facebook_links, twitter_links=twitter_links, instagram_links=instagram_links)

@app.route("/analysen")
def analysen():
    return render_template('analysen.html')

@app.route("/analysen/twitter_nutzung")
def analysen_twitter_nutzung():
    return render_template('twitter_nutzung.html')

@app.route("/analysen/tweet_themen")
def analysen_tweet_themen():
    return render_template('tweet_themen.html')

#Checks if the run.py file has executed directly and not imported
if __name__ == '__main__':
    app.run(debug=True)


