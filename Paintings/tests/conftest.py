import pytest 
from Paintings.App import create_app 


def pytest_unconfigure(config):
    """Delete all images in the test db and remove associated files
       This gets called at the end of the test run
     """
    from pathlib import Path
    import config
    from instance import test_config
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from Paintings.models.public import (Series, Image, Contact)

    img_root = Path(config.STATIC_IMAGE_ROOT)
    thumb_root = Path(config.STATIC_THUMBNAIL_ROOT)
    
    db_uri = test_config.SQLALCHEMY_DATABASE_URI
    test_engine = create_engine(db_uri)
    Session = sessionmaker(bind=test_engine)
    session = Session()
    
    images = session.query(Image).all()
    
    for i in images:
        img_path = Path(img_root, i.filename)
        thumb_path = Path(thumb_root, i.filename)

        if img_path.exists():
            img_path.unlink()
        if thumb_path.exists():
            thumb_path.unlink()

        session.delete(i)

    series = session.query(Series).all()
    for i in series:
        session.delete(i)

    # delete contact_info
    contact_info = session.query(Contact).all()
    for i in contact_info:
        session.delete(i)

    session.commit()


@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(session, config, items):
    # image tests need a series, so series tests need to be done first
    # ... tests probably shouldn't rely on data from previous tests...
    items = sorted(items, key=lambda i: 'series' not in i.name)
    session.items = items


@pytest.fixture(scope='session')
def app():
    """fixture for app object"""

    app = create_app('test_config.py')
    app.testing = True
    return app


