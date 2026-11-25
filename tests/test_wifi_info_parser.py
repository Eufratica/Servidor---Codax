"""
Teste isolado do parser puro de auditoria Wi-Fi / Roteador / Canal (sem MQTT/rede).
Executar:  python tests/test_wifi_info_parser.py
"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import parse_device_info_payload, parse_disabled_tabs  # noqa: E402

# Payload REAL capturado em 25/11/2026 de dev/retorno/shopba/mesh/704bca491df8 (query info)
REAL_QUERY_INFO = {
    "timestamp": "Wed Nov 25 17:12:31 2026",
    "root": "70:4b:ca:49:1d:f8(70:4b:ca:49:1d:f8)",
    "addr": "70:4b:ca:49:1d:f8(70:4b:ca:49:1d:f8)",
    "times": 1795626751,
    "timezone": "UTC -03:00",
    "data": {
        "id": "70:4b:ca:49:1d:f8",
        "parent_id": "0",
        "device_settings": "device_id: 70:4b:ca:49:1d:f8, router_ssid: LEDAXIO_DEV, router_password: secret, mesh_id:00:00:00:00:44:07",
        "ip": "ip_new: 192.168.1.102, gw_new: 192.168.0.1, ip_old: 192.168.1.102, gw_old: 192.168.0.1",
        "network": "circuitID: 70:4b:ca:49:1d:f8, router_ssid: LEDAXIO_DEV, router_password: secret, mesh_id: 00:00:00:00:44:07, mesh_password: pwd, channel: 6",
        "system": "layer: 1, self mac: 70:4b:ca:49:1d:f8, parent bssid: bc:07:1d:57:11:75, parent rssi: -38, node num: 1, free heap: 46828, root status: 1, mesh_type: 1, i'm root: 1, self_org: 1, fix_root: 0, parent connected: 1",
    },
}

# Payload REAL de query network
REAL_QUERY_NETWORK = {
    "root": "70:4b:ca:49:1d:f8(70:4b:ca:49:1d:f8)",
    "addr": "70:4b:ca:49:1d:f8(70:4b:ca:49:1d:f8)",
    "data": {
        "id": "70:4b:ca:49:1d:f8",
        "parent_id": "0",
        "network": {
            "ssid": "LEDAXIO_DEV",
            "password": "secret",
            "device_obj_ssid": "LEDAXIO_DEV",
        },
    },
}


def test_real_query_info():
    p = parse_device_info_payload(REAL_QUERY_INFO)
    assert p is not None
    assert p["mac"] == "704bca491df8"
    assert p["root_mac"] == "704bca491df8"
    assert p["router_ssid"] == "LEDAXIO_DEV"
    assert p["channel"] == 6
    assert p["router_mac"] == "bc071d571175"
    assert p["parent_bssid"] == "bc071d571175"
    assert p["parent_rssi"] == -38
    assert p["layer"] == 1
    assert p["is_root"] is True
    assert p["parent_connected"] is True
    assert p["ip"] == "192.168.1.102"
    assert p["gw"] == "192.168.0.1"


def test_real_query_network():
    p = parse_device_info_payload(REAL_QUERY_NETWORK)
    assert p is not None
    assert p["mac"] == "704bca491df8"
    assert p["router_ssid"] == "LEDAXIO_DEV"


def test_child_node_does_not_overwrite_router_mac():
    child_payload = {
        "root": "70:4b:ca:49:1d:f8",
        "addr": "30:83:98:63:50:b0",
        "data": {
            "network": "router_ssid: LEDAXIO_DEV, channel: 11",
            "system": "layer: 2, self mac: 30:83:98:63:50:b0, parent bssid: 70:4b:ca:49:1d:f9, parent rssi: -55, i'm root: 0, parent connected: 1",
        },
    }
    p = parse_device_info_payload(child_payload)
    assert p is not None
    assert p["is_root"] is False
    assert p["channel"] == 11
    assert "router_mac" not in p
    assert p["parent_bssid"] == "704bca491df9"


def test_ignores_non_info_payloads():
    assert parse_device_info_payload({"data": {"message": "hb parent=bc:07:1d:57:11:75 layer=1 rssi=-40"}}) is None
    assert parse_device_info_payload("texto") is None
    assert parse_device_info_payload({}) is None


def test_disabled_tabs_parser():
    assert parse_disabled_tabs("ota,serial,webserver,timestream,scifi") == [
        "ota", "serial", "webserver", "timestream", "scifi"
    ]
    assert parse_disabled_tabs("") == []


if __name__ == "__main__":
    test_real_query_info()
    test_real_query_network()
    test_child_node_does_not_overwrite_router_mac()
    test_ignores_non_info_payloads()
    test_disabled_tabs_parser()
    print("ALL WIFI INFO PARSER TESTS PASSED!")
