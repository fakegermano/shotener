from unittest import TestCase
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from hypothesis import given, strategies as st, provisional as pv, settings, Verbosity
from fastapi.testclient import TestClient
from main import app, get_db, Base

DATABASE_URL = "sqlite:///./test.db"

class TestUrlShortener(TestCase):
    def setUp(self) -> None:
        self.engine = create_engine(
            DATABASE_URL, connect_args={"check_same_thread": False}
        )

        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        Base.metadata.create_all(bind=self.engine)

        def override_get_db():
            db = TestingSessionLocal()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db

        self.client = TestClient(app)

        return super().setUp()

    def tearDown(self) -> None:
        Base.metadata.drop_all(bind=self.engine)
        return super().tearDown()
    
    @settings(max_examples=100, verbosity=Verbosity.verbose, deadline=None)
    @given(url=pv.urls())
    def test_url_shortener(self, url):
        response = self.client.post("/", json={"url": url})
        assert response.status_code == 200
        assert len(response.content.decode().replace(self.client.base_url + "/", "")) == 8

    @settings(max_examples=100, verbosity=Verbosity.verbose, deadline=None)
    @given(url=pv.urls())
    def test_url_expander(self, url):
        response = self.client.post("/", json={"url": url})
        key = response.content.decode().replace(self.client.base_url + "/", "")
        response = self.client.get(f"{key}", allow_redirects=False)
        assert response.status_code == 302