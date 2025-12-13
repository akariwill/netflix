from flask import Flask, render_template, jsonify
import pandas as pd

app = Flask(__name__)

df = pd.read_csv('data/data_netflix_bersih_uas.csv')

@app.route('/')
def index():
    movie_count = df[df['type'] == 'Movie'].shape[0]
    tv_show_count = df[df['type'] == 'TV Show'].shape[0]
    kpis = {
        'Total Film': movie_count,
        'Total Acara TV': tv_show_count
    }
    return render_template('index.html', tables=[df.to_html(classes='data table table-striped table-dark table-hover', index=False)], titles=df.columns.values, kpis=kpis)

@app.route('/api/data/type')
def data_type():
    type_counts = df['type'].value_counts().to_dict()
    return jsonify(type_counts)

@app.route('/api/data/release_year')
def data_release_year():
    year_counts = df['release_year'].value_counts().sort_index(ascending=False).head(20).sort_index()
    return jsonify(year_counts.to_dict())

@app.route('/api/data/country')
def data_country():
    country_counts = df['country'].value_counts().head(10)
    return jsonify(country_counts.to_dict())

if __name__ == '__main__':
    app.run(debug=True)
