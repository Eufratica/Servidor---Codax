"""
Teste isolado da varredura de Autodescoberta (função pura, sem conectar ao broker).
Executar:  python tests/test_discovery_messages.py
Obs.: importa app.py, que cria o cliente MQTT mas só conecta no startup do FastAPI.
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import app  # noqa: E402


def summarize(msgs):
    return [(t, p["addr"][0], p["data"]["function"], p.get("for_mesh", False)) for t, p in msgs]


def test_aws_mode_sends_readonly_queries_to_prod_and_dev():
    msgs = summarize(app.build_discovery_messages("AWS"))
    assert ("config/shopba/mesh", "ff0000010000", "topology", False) in msgs
    assert ("dev/config/shopba/mesh", "ff0000010000", "topology", False) in msgs
    assert ("config/shopba/mesh", "ffffffffffff", "ping", True) in msgs
    assert ("dev/config/shopba/mesh", "ffffffffffff", "ping", True) in msgs
    assert len(msgs) == 4


def test_local_mode_keeps_previous_behaviour():
    msgs = summarize(app.build_discovery_messages("LOCAL"))
    assert ("dev/config/shopba/mesh", "ffffffffffff", "topology", True) in msgs
    assert len(msgs) == 6


def test_only_query_methods():
    for mode in ("AWS", "LOCAL"):
        for _, payload in app.build_discovery_messages(mode):
            assert payload["data"]["method"] == "query"


def test_online_window_covers_heartbeat_interval():
    import time
    node = {"last_seen_epoch": time.time() - 265}  # maior intervalo de heartbeat medido (ROOT)
    assert app.is_node_online(node)
    assert not app.is_node_online({"last_seen_epoch": time.time() - (app.NODE_ONLINE_THRESHOLD_SECONDS + 5)})


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for fn in tests:
        fn()
        print(f"OK  {fn.__name__}")
    print(f"\n{len(tests)} testes passaram.")
