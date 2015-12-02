import uuid
from pathlib import Path
from flask import (current_app, url_for) 
from lxml import (html, etree)
import pytest
from Paintings.core import db
from Paintings.models.public import (Series, Image)


class TestImage():
    """These tests require a series present in the database """
    def test_get_image(self, client):
        """Make sure admin/newimage view works"""
        series = db.session.query(Series).first()
        assert series
        url = url_for('Admin.new_image', series_id=series.id)
        resp = client.get(url)
        assert resp.status_code == 200

        data = html.fromstring(resp.data)

        id_elem = data.xpath('//input[@id="id"]')
        img_id = id_elem[0].value
        assert img_id


    def test_post_image(self, client):
        """Add a new image with valid data"""
        series = db.session.query(Series).first()
        url = url_for('Admin.new_image', series_id=series.id)

        img_path = Path('Paintings/tests/test_data/test_image.jpg').resolve()
        assert img_path.exists()
        filename = str(img_path.name)

        post_data = {'title':'Untitled',
                     'series_id':str(series.id),
                     'id':str(uuid.uuid4()),
                     'date':'2015',
                     'padding_color':'#ffffff',
                     'dimensions-0':'21',
                     'dimensions-1':'27',
                     'medium':'bytes on disk',
                     'image':(str(img_path), filename)
                    }

        resp = client.post(url, data=post_data, follow_redirects=True)

        data = html.fromstring(resp.data)
        messages = data.xpath("//ul[@class='messages']/li")
        message_text = ''.join([etree.tostring(i, encoding=str) for i in messages])
        assert 'Untitled' in message_text
        assert 'added to ' in message_text

        id_elem = data.xpath('//input[@id="id"]')
        img_id = id_elem[0].value
        assert img_id

        image = db.session.query(Image).get(img_id)

        img_path = Path(current_app.config.get('STATIC_IMAGE_ROOT'), image.filename)
        thumb_path = Path(current_app.config.get('STATIC_THUMBNAIL_ROOT'), image.filename)
        assert img_path.exists()
        assert thumb_path.exists()


    def test_get_edit_image(self, client):
        image = db.session.query(Image).first()
        assert image
        url = url_for('Admin.edit_image', image_id=image.id)
        resp = client.get(url)
        assert resp.status_code == 200


    def test_post_edit_image(self, client):
        """modify existing image record with valid data"""
        image = db.session.query(Image).first()
        assert image
        url = url_for('Admin.edit_image', image_id=image.id)

        post_data = {'title':'Untitled 2',
                     'series_id':image.series_id,
                     'id':image.id,
                     'date':'2014',
                     'padding_color':'#000000',
                     'dimensions-0':'27',
                     'dimensions-1':'21',
                     'medium':'Digital Imagery',
                    }

        resp = client.post(url, data=post_data, follow_redirects=True)
        assert resp.status_code == 200

        data = html.fromstring(resp.data)
        messages = data.xpath("//ul[@class='messages']/li")
        message_text = ''.join([etree.tostring(i, encoding=str) for i in messages])
        assert "Untitled 2" in message_text
        assert 'has been changed' in message_text 


    @pytest.mark.trylast
    @pytest.mark.addoption(TRAP_HTTP_EXCEPTIONS=True)
    def test_delete_image(self, client):
        """add an image and then delete it
            Requires auth token
            Unfortunately, it seems like there's no (easy) way to
            deactivate or fake the auth token
        """
