from desktop import LocalApplicationServer, smoke_test


def test_desktop_server_uses_ephemeral_loopback_port():
    local = LocalApplicationServer()
    try:
        assert local.port > 0
        assert local.url.startswith("http://127.0.0.1:")
    finally:
        local.shutdown()


def test_desktop_smoke_test():
    assert smoke_test() == 0
