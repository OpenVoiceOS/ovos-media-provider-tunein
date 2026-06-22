# ovos-media-provider-tunein

OVOS **MediaProvider** plugin for [TuneIn](https://tunein.com). Replaces the
deprecated OCP search skill `ovos-skill-tunein`.

It wraps the [`tunein`](https://github.com/TigreGotico/tunein) client, which
emits [`mediavocab.Release`](https://github.com/TigreGotico/mediavocab) objects
directly, and exposes TuneIn's public radio/podcast/IPTV station search to the
OCP pipeline.

## Routing

| Axis | Value |
| --- | --- |
| `media` | `{MediaType.RADIO}` |
| `playback_type` | `{PlaybackType.AUDIO}` |

The pipeline gates this provider out of non-radio queries before paying for a
network search.

## Install

```bash
pip install ovos-media-provider-tunein
```

The plugin is registered under the `opm.media.provider` entry-point group as
`tunein` and is loaded in-process by the OCP pipeline; there is nothing to
configure.

### Configuration

| Key | Default | Description |
| --- | --- | --- |
| `enrich` | `false` | Issue a per-station `Describe.ashx` call to populate genre, language, country, call-sign and slogan. Off by default to keep search cheap. |

## How it works

`TuneInMediaProvider.search(signals, lang)` builds a query from `signals.title`,
calls `tunein.TuneIn.search(...)`, and returns the `mediavocab.Release` produced
by each station's `to_release()`. Per mediavocab axiom 8 (station identity), a
TuneIn channel is a `Work` with `MediaType.RADIO` and the playable stream URL is
a `Release` with `StreamMode.CONTINUOUS` (live linear broadcast). A station may
expose several stream URLs (bitrates/protocols), each yielding its own
`Release`; the OCP pipeline filters and ranks across providers.

## License

Apache-2.0
