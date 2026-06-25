"""Unit tests for TuneInMediaProvider (network mocked)."""
from unittest.mock import MagicMock, patch

from mediavocab import MediaType, Release, Signals, StreamMode, Work

from ovos_media_provider_tunein import TuneInMediaProvider


def _make_release(title):
    return Release(
        work=Work(title=title, media_type=MediaType.RADIO),
        uri=f"http://stream.example/{title}",
        stream_mode=StreamMode.CONTINUOUS,
    )


def _make_station(title):
    station = MagicMock()
    station.to_release.return_value = _make_release(title)
    return station


def test_instantiation():
    prov = TuneInMediaProvider()
    assert prov.name == "tunein"


def test_search_returns_releases():
    prov = TuneInMediaProvider()
    stations = [_make_station("BBC Radio 4"), _make_station("Radio Paradise")]
    with patch("ovos_media_provider_tunein.TuneIn.search",
               return_value=iter(stations)) as mocked:
        results = prov.search(
            Signals(medium=MediaType.RADIO, title="bbc radio 4"),
            lang="en-us",
            supported_playback_types={"audio"},
            blocked_genres={"adult"},
            region="GB",
            session_id="sess-1",
        )
    mocked.assert_called_once()
    assert isinstance(results, list)
    assert len(results) == 2
    assert all(isinstance(r, Release) for r in results)
    assert results[0].work.title == "BBC Radio 4"


def test_search_empty_query():
    prov = TuneInMediaProvider()
    with patch("ovos_media_provider_tunein.TuneIn.search") as mocked:
        results = prov.search(Signals(medium=MediaType.RADIO))
    mocked.assert_not_called()
    assert results == []


def test_search_swallows_per_item_errors():
    prov = TuneInMediaProvider()
    bad = MagicMock()
    bad.to_release.side_effect = RuntimeError("boom")
    good = _make_station("ok")
    with patch("ovos_media_provider_tunein.TuneIn.search",
               return_value=iter([bad, good])):
        results = prov.search(Signals(medium=MediaType.RADIO, title="anything"))
    assert [r.work.title for r in results] == ["ok"]
