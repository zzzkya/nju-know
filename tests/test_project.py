import os, tempfile, unittest
from pathlib import Path
from unittest.mock import patch

class SiteTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        import app
        self.app = app
        self.patcher = patch.object(app, 'DB_PATH', Path(self.tmp.name) / 'test.sqlite3')
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        app.init_db()
    def test_health(self):
        with self.app.app.test_client() as c:
            self.assertEqual(c.get('/health').json['status'], 'ok')
    def test_empty_page(self):
        with self.app.app.test_client() as c:
            self.assertIn('这里还没有信息', c.get('/').get_data(as_text=True))
    def test_search_and_category(self):
        with self.app.connect() as db:
            db.execute("INSERT INTO posts(title,source,source_url,published_date,category) VALUES(?,?,?,?,?)", ('AI讲座','学院','https://example.com/a','2026-10-20','学术'))
        self.assertEqual(len(self.app.get_posts('AI','学术')),1)
        self.assertEqual(len(self.app.get_posts('AI','教务')),0)

if __name__ == '__main__': unittest.main()
