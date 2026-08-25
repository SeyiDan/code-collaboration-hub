# 👥 Code Collaboration Hub

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![Socket.IO](https://img.shields.io/badge/Socket.IO-Real--time-orange.svg)](https://socket.io/)
[![Docker](https://img.shields.io/badge/Docker-Supported-blue.svg)](https://www.docker.com/)

A Flask web app where several people can open the same project and edit its code together.
Edits are broadcast over WebSockets and permission-checked on the server before they are applied.

**Be clear about the granularity:** a save broadcasts, not a keystroke. Clicking Save emits
`code_update`; other viewers receive `code_updated` and reload. This is collaborative editing at
save granularity, not character-by-character like Google Docs.

**12 Flask routes, 6 Socket.IO event handlers, 3 SQLAlchemy models.**

## What it actually does

- **Accounts and sessions** — register, log in, log out, managed by Flask-Login.
- **Projects** — create, view, edit, delete, plus a dashboard of your own and an explore page.
- **Collaborators with permission levels** — a project owner can add and remove collaborators,
  each holding `read`, `write` or `admin`.
- **Shared editing** — `code_update` broadcasts a saved document to everyone in the project room.
  A `cursor_position` handler exists on the server but **no template emits or listens for it**, so
  cursor sharing is wired but not reachable from the UI.
- **Server-side authorization on every edit** — see below. This is the part worth reading.
- **Syntax highlighting** — server-side via Pygments. The editing surface itself is a plain
  `<textarea>` wired to Socket.IO, not a client-side editor component.

## How the live editing works, and what it does not do

Every `code_update` is authorized before anything is written or broadcast
(`app/sockets/events.py`):

```python
if project.owner_id == current_user.id:
    can_edit = True
else:
    for collab in project.collaborations:
        if collab.user_id == current_user.id and collab.permission in ['write', 'admin']:
            can_edit = True
            break
if not can_edit:
    return
```

A read-only collaborator can open the socket, join the room and emit an edit, and the server
drops it. Authorization is not left to the client.

**The honest limit: this is last-write-wins on the whole document.** The handler assigns
`project.content = content`, commits, and broadcasts. There is **no operational transform, no
CRDT, no merge and no diff.** Two people typing in different parts of the same file at the same
moment will have one of them overwrite the other. Real concurrent editing needs OT or a CRDT,
and I did not implement one.

That is a genuine limitation and it is stated here rather than described as "conflict
resolution", which is what an earlier version of this README claimed and the code never did.

## 🛠 Tech Stack

**Backend:** Python 3.8+, Flask, Flask-SocketIO, Flask-Login, SQLAlchemy
**Frontend:** JavaScript, Socket.IO client, and a plain `<textarea>`. There is no editor
library: no CodeMirror, no Ace, no Monaco. An earlier version of this README named CodeMirror,
which was never in the dependency list or the templates.
**Highlighting:** Pygments, server-side
**Database:** SQLite by default, PostgreSQL under Docker Compose
**Deployment:** Docker, Docker Compose

## Data model

| Model | Purpose |
|---|---|
| `User` | account, credentials, session identity |
| `Project` | owner, name, language, and the document `content` itself |
| `Collaboration` | join row between a user and a project, carrying the permission level |

## Socket.IO events

| Event | Direction | Purpose |
|---|---|---|
| `connect` / `disconnect` | client to server | session lifecycle |
| `join` / `leave` | client to server | enter or exit a `project_<id>` room |
| `code_update` | client to server | submit an edit; authorized, persisted, rebroadcast as `code_updated` |
| `cursor_position` | client to server | share caret position with the room |

## Installation

### Prerequisites

- Python 3.8 or newer
- pip
- Docker and Docker Compose (optional)

### Without Docker

```bash
git clone https://github.com/SeyiDan/code-collaboration-hub.git
cd code-collaboration-hub
python -m venv venv
source venv/bin/activate        # venv\Scripts\activate on Windows
pip install -r requirements.txt
python app.py
```

Open http://localhost:8080.

**Use `app.py`, not `run.py`.** `run.py` calls `app.run()` rather than `socketio.run()`, so it
starts the server with WebSockets disabled, which is the one feature this project exists for.
Its own docstring says "without SocketIO".

### With Docker

```bash
docker-compose up --build
```

## Project Structure

```bash
├── app/
│   ├── models/          # User, Project, Collaboration
│   ├── routes/          # auth.py (register/login/logout), main.py (projects)
│   └── sockets/         # events.py, the 6 Socket.IO handlers
├── templates/           # Jinja2 views
├── tests/
│   └── test_models.py   # 6 model tests
├── docker-compose.yml
└── run.py
```

## Running Tests

```bash
python -m pytest tests/
```

Six tests, all covering the models. **This suite does not cover the socket handlers**, which is
where the authorization logic lives, so the most important code in the project is currently the
least tested. That is the first thing I would add.

## 🔒 Security notes

- Passwords are hashed, never stored in plaintext.
- Sessions are managed by Flask-Login. The four handlers that touch project data (`join`, `leave`,
  `code_update`, `cursor_position`) re-check `current_user.is_authenticated` rather than trusting
  the connection. `connect` and `disconnect` do not; `connect` replies to any socket with a
  constant.
- Edit authorization is enforced server-side, per project, on every `code_update`.

**Not implemented**, and listed here so nobody assumes otherwise: CSRF tokens, rate limiting,
audit logging. A previous version of this README claimed all three.

## 📝 License

MIT. See [LICENSE](LICENSE).
