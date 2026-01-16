from app.main import app


def test_toolbox_route_registered() -> None:
    paths = {route.path for route in app.routes}
    assert "/toolbox" in paths
