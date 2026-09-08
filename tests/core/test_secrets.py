from hermes.core.secrets import SecretStore, get_secret


def test_secret_store_set_get():
    store = SecretStore()
    store.set("test_key", "test_value")
    assert store.get("test_key") == "test_value"


def test_secret_store_get_default():
    store = SecretStore()
    assert store.get("missing", "default") == "default"


def test_secret_store_get_missing():
    store = SecretStore()
    assert store.get("missing") is None


def test_global_get_secret():
    # Test module-level helper
    assert get_secret("global_key") is None
