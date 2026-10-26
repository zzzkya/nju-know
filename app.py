import os
import sqlite3
from pathlib import Path
from flask import Flask, render_template, request, jsonify

ROOT = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get('NJU_DB_PATH', str(ROOT / 'nju_know.sqlite3')))
app = Flask(__name__)


def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db


def init_db():
    with connect() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            source TEXT NOT NULL,
            source_url TEXT NOT NULL UNIQUE,
            published_date TEXT,
            event_date TEXT,
            category TEXT NOT NULL DEFAULT '其他',
            summary TEXT NOT NULL DEFAULT '',
            collected_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )''')
        db.execute('CREATE INDEX IF NOT EXISTS idx_posts_date ON posts(published_date DESC)')
        db.execute('CREATE INDEX IF NOT EXISTS idx_posts_category ON posts(category)')


def get_posts(q='', category='全部', limit=100):
    sql = 'SELECT * FROM posts WHERE 1=1'
    params = []
    if q:
        sql += ' AND (title LIKE ? OR source LIKE ? OR summary LIKE ?)'
        like = f'%{q}%'
        params.extend([like, like, like])
    if category != '全部':
        sql += ' AND category = ?'
        params.append(category)
    sql += ' ORDER BY published_date DESC, id DESC LIMIT ?'
    params.append(min(max(limit, 1), 200))
    with connect() as db:
        return [dict(row) for row in db.execute(sql, params)]


@app.route('/')
def home():
    return render_template('index.html', posts=get_posts(request.args.get('q','').strip(), request.args.get('category','全部')), q=request.args.get('q',''), category=request.args.get('category','全部'))


@app.route('/api/posts')
def api_posts():
    return jsonify({'items': get_posts(request.args.get('q','').strip(), request.args.get('category','全部')), 'note':'published_date is publication date, not event date'})


@app.route('/health')
def health():
    return jsonify(status='ok')


if __name__ == '__main__':
    init_db()
    app.run(host='127.0.0.1', port=int(os.environ.get('PORT', 5000)), debug=os.environ.get('FLASK_DEBUG') == '1')
