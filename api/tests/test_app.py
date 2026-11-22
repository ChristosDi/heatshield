def test_tests_use_an_in_memory_database(app):
    assert app.testing
    assert app.config["SQLALCHEMY_DATABASE_URI"] == "sqlite:///:memory:"