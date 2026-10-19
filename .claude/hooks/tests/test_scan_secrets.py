from scan_secrets import scan


def test_finds_secrets():
    assert scan("key = 'fk_live_ab12cd34_" + "x" * 32 + "'")
    assert scan("-----BEGIN RSA PRIVATE KEY-----")
    assert scan("postgres://admin:supersecret99@db/prod")


def test_ignores_local_dev_url_and_placeholders():
    assert scan("postgresql+asyncpg://fitment:fitment@localhost:5432/fitment") == []
    assert scan("ADMIN_TOKEN=") == []
