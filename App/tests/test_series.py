import uuid
from flask import current_app, url_for
from lxml import html, etree

from App.core import db
from App.models.public import Series

class TestSeries:
    def test_get_newseries(self, client):
        'Make sure admin/series view works'
        url = url_for('Admin.newseries')
        resp = client.get(url)
        assert resp.status_code == 200
        data = html.fromstring(resp.data)
        _id = data.xpath('//input[@id="id"]')
        assert len(_id)


    def test_post_newseries(self, client):
        'Test if series is added correctly with valid data '
        url = url_for('Admin.newseries')
        
        _id = str(uuid.uuid4())
        series_title = 'test series'
        
        post_data = {'title':series_title, 'id':_id}
        resp = client.post(url, 
                           data=post_data, 
                           follow_redirects=True)
        
        data = html.fromstring(resp.data)
        
        message_elems = data.xpath('//ul[@class="messages"]/li')
        assert len(message_elems)

        messages = ''.join([str(etree.tostring(i)) for i in message_elems])
        assert series_title in messages

        series_q = db.session.query(Series)
        series = series_q.get(_id)
        assert series.title == series_title
        assert str(series.id) == _id

    def test_get_editseries(self, client):
        'Make sure admin/editseries view works'
        series = db.session.query(Series).first()
        assert series

        url = url_for('Admin.edit_series', _id=series.id)
        resp = client.get(url)
        assert resp.status_code == 200

    def test_post_editseries(self, client):
        'Change the title of an existing series '
        series = db.session.query(Series).first()
        url = url_for('Admin.edit_series', _id=series.id)
        new_title = 'new series title'

        post_data = {'title':new_title, 'id':series.id, 'order':series.order}
        resp = client.post(url, data=post_data, follow_redirects=True)

        data = html.fromstring(resp.data)
        messages = data.xpath("//ul[@class='messages']/li/descendant::*")
        li = data.xpath("//ul[@class='messages']/li")
        messages = ''.join([etree.tostring(i, encoding=str) for i in li])
        assert new_title in messages
