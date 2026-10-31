# SyLog – Symptom Logger

A small self-hosted web app for logging symptoms, built with [NiceGUI](https://nicegui.io) and SQLite.

<!-- screenshot -->

## Features

- Log a symptom with date, time, severity and a description
- Pick from a predefined list or add your own symptoms
- Browse and filter history, delete entries
- Export the log to CSV

## Run

Requires [uv](https://docs.astral.sh/uv/) and Python 3.13+.

```sh
uv sync
uv run sylog/main.py
```

The app is served at <http://localhost:8080>.

## Docker

```sh
docker compose up -d --build
```

The app is served at <http://localhost:3435>. 

## Data

| Path       | Content                  |
|------------|--------------------------|
| `data/`    | SQLite database          |
| `log/`     | Application logs         |
| `exports/` | Generated CSV exports    |

## License

See [LICENSE](LICENSE).
