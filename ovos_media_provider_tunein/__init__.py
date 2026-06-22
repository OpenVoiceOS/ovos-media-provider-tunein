"""TuneIn MediaProvider plugin for OVOS.

Wraps the :mod:`tunein` client and exposes TuneIn radio search to the OCP
pipeline as a
:class:`~ovos_plugin_manager.templates.media_provider.MediaProvider`.
Replaces the deprecated OCP search skill ``ovos-skill-tunein``.

``tunein`` already emits :class:`mediavocab.Release` objects: each
``TuneInStation`` returned by ``TuneIn.search`` exposes a ``to_release()``
mapping a live linear radio stream into a ``mediavocab.Release`` with
``MediaType.RADIO`` / ``StreamMode.CONTINUOUS``. This provider is a thin
routing/filtering shim over that public search API.
"""
from typing import ClassVar, List, Optional, Set

from ovos_utils.log import LOG

from mediavocab import MediaType, Release, Signals
from mediavocab.taxonomy import PlaybackType

from ovos_plugin_manager.templates.media_provider import MediaProvider

from tunein import TuneIn

from ovos_media_provider_tunein.version import __version__  # noqa: F401


class TuneInMediaProvider(MediaProvider):
    """Search TuneIn and return playable radio :class:`Release` objects.

    Routing is fixed to radio audio: the OCP pipeline gates this provider out
    of non-radio queries before paying for a network search.
    """

    name: ClassVar[str] = "tunein"
    media: ClassVar[Set[MediaType]] = {MediaType.RADIO}
    playback_type: ClassVar[Set[PlaybackType]] = {PlaybackType.AUDIO}

    def __init__(self, config: Optional[dict] = None):
        super().__init__(config)
        # opt into the per-station Describe.ashx enrichment call (genre,
        # language, country, call-sign, ...). Off by default to keep search
        # cheap; overridable via plugin config.
        self.enrich: bool = bool(self.config.get("enrich", False))

    def is_available(self) -> bool:
        """``tunein`` is a hard dependency and TuneIn's search endpoint needs
        no API key, so the provider is available whenever its imports
        resolved."""
        return True

    def search(self, signals: Signals, lang: str = "en-us") -> List[Release]:
        """Search TuneIn for ``signals.title`` and return candidate radio
        :class:`Release` objects.

        Each ``TuneInStation`` yielded by ``TuneIn.search`` carries a
        ``to_release()`` mapping the live stream into a ``mediavocab.Release``;
        a station can expose several stream URLs (bitrates/protocols), so a
        single query may yield multiple releases.
        """
        query = (signals.title or "").strip()
        if not query:
            return []

        releases: List[Release] = []
        try:
            for station in TuneIn.search(query, enrich=self.enrich):
                try:
                    releases.append(station.to_release())
                except Exception:
                    LOG.exception("Failed to convert TuneIn station to Release")
        except Exception:
            LOG.exception(f"TuneIn search failed for query: {query!r}")
            return []
        return releases
