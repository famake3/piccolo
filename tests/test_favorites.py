from src.favorites import FavoritesManager


def test_add_and_remove(tmp_path):
    path = tmp_path / "favorites.json"
    mgr = FavoritesManager(path)
    mgr.add("red", 255, 0, 0)
    assert len(mgr.list()) == 1
    fav = mgr.get("red")
    assert fav and fav.r == 255 and fav.g == 0 and fav.b == 0
    mgr.remove("red")
    assert mgr.get("red") is None
