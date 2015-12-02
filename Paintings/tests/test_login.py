
from flask import current_app, url_for
import lxml.html
import pytest


class TestLogin():
    def test_get_login(self, client):
        url = url_for('Admin.login')
        resp = client.get(url)
        assert resp.status_code == 200

    @pytest.mark.options(LOGIN_DISABLED=False)
    def test_post_valid_login(self, client):
        url = url_for('Admin.login')
        username = current_app.config.get('TEST_USERNAME')
        password = current_app.config.get('TEST_PASSWORD')

        resp = client.post(url, 
                           data={'username':username, 
                                 'password':password})
       
        assert resp.status_code == 302

        html = lxml.html.fromstring(resp.data)
        link = html.xpath('//a[@href]')
        assert link[0].text == url_for('Admin.index')

    
    @pytest.mark.options(LOGIN_DISABLED=False)
    def test_post_invalid_login(self, client):
        url = url_for('Admin.login')
        username = 'invalidUsername'
        password = 'bad_passw0rd'

        resp = client.post(url, 
                           data={'username':username, 
                                 'password':password})
       
        assert resp.status_code == 302

        html = lxml.html.fromstring(resp.data)
        link = html.xpath('//a[@href]')
        assert link[0].text == url_for('Admin.login')
