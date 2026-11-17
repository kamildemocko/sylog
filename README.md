# SyLog – Symptom Logger

A small self-hosted web app for logging symptoms, built with [NiceGUI](https://nicegui.io) and SQLite.

<!-- screenshot -->

## Features

- Log a symptom with date, time, severity and a description
- Log daily context
- Pick from a predefined list or add your own symptoms
- Browse and filter history, delete entries
- Export the log to CSV
- Backup database

## Screenshot
<img width="712" height="1033" alt="image" src="https://github.com/user-attachments/assets/2cc14f41-6b3a-4a92-82e1-8baafcd49cd7" />



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
