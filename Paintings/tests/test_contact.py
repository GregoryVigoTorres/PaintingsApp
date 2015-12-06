import uuid
from flask import current_app, url_for
from lxml import html, etree

from Paintings.core import db
from Paintings.models.public import Contact

from .utils import get_messages

class TestContact:
    def test_get_contact(self, client):
        url = url_for('Admin.contact')
        resp = client.get(url)
        assert resp.status_code == 200


    def test_new_contact(self, client):
        url = url_for('Admin.new_contact')
        name = 'new_name'
        _id = str(uuid.uuid4())

        data = {'name':name,
                'url':'https://thiisaurl.com',
                'id':_id}

        resp = client.post(url, data=data, follow_redirects=True)
        assert resp.status_code == 200

        messages = get_messages(resp.data)
        assert name in messages


    def test_edit_contact(self, client):
        ci = db.session.query(Contact).first()
        assert ci
    
        _id = ci.id

        url = url_for('Admin.edit_contact', _id=_id)
        assert url

        name = 'this name has been changed'
        data = {'name':name,
                'url':'http://www.invalidurl.org',
                'id':_id}

        resp = client.post(url, data=data, follow_redirects=True)
        assert resp.status_code == 200

        messages = get_messages(resp.data)
        assert name in messages
        assert 'has been updated' in messages
