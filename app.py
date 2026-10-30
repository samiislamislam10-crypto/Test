import os, re, sqlite3, secrets, subprocess, signal, sys, time, shutil, zipfile
from pathlib import Path
from functools import wraps
from flask import Flask, request, redirect, url_for, session, flash, render_template, send_file, abort

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
USERS = DATA / "users"
DEFAULT_FILES = DATA / "default_files"
DB = DATA / "panel.db"
DATA.mkdir(exist_ok=True)
USERS.mkdir(exist_ok=True)
DEFAULT_FILES.mkdir(exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ.get("PANEL_SECRET", secrets.token_hex(32))
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax",
                  MAX_CONTENT_LENGTH=20 * 1024 * 1024)

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin INTEGER NOT NULL DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )""")
        con.execute("""CREATE TABLE IF NOT EXISTS servers(
            user_id INTEGER PRIMARY KEY,
            pid INTEGER,
            status TEXT DEFAULT 'STOPPED',
            script TEXT,
            started_at REAL,
            log_file TEXT
        )""")
        count = con.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if count == 0:
            from werkzeug.security import generate_password_hash
            # First account is admin; set credentials through environment before first run.
            username = os.environ.get("PANEL_ADMIN_USER", "admin")
            password = os.environ.get("PANEL_ADMIN_PASSWORD", "ChangeMe123!")
            con.execute("INSERT INTO users(username,password_hash,is_admin) VALUES(?,?,1)",
                        (username, generate_password_hash(password)))

def user_dir(uid):
    p = USERS / str(uid)
    p.mkdir(parents=True, exist_ok=True)
    return p

def safe_user_path(uid, rel=""):
    base = user_dir(uid).resolve()
    target = (base / rel).resolve()
    if target != base and base not in target.parents:
        abort(403)
    return target

def copy_default_files(uid):
    """Recursively copy shared defaults (including folders such as Pb2) to a user.

    Missing files are added for both new and existing users. Existing user files
    are never overwritten, and symlinks are ignored for safety.
    """
    destination = user_dir(uid)

    def copy_tree_missing(source_dir, target_dir):
        target_dir.mkdir(parents=True, exist_ok=True)
        for source in source_dir.iterdir():
            if source.is_symlink():
                continue
            target = target_dir / source.name
            if source.is_dir():
                copy_tree_missing(source, target)
            elif source.is_file() and not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)

    copy_tree_missing(DEFAULT_FILES, destination)


def current_user():
    if not session.get("uid"):
        return None
    with db() as con:
        return con.execute("SELECT * FROM users WHERE id=?", (session["uid"],)).fetchone()

def login_required(fn):
    @wraps(fn)
    def wrapped(*a, **kw):
        if not current_user():
            return redirect(url_for("login"))
        return fn(*a, **kw)
    return wrapped

def valid_name(name):
    return bool(re.fullmatch(r"[A-Za-z0-9_.-]{1,64}", name or "")) and name not in (".", "..")

def server_row(uid):
    with db() as con:
        row = con.execute("SELECT * FROM servers WHERE user_id=?", (uid,)).fetchone()
    if row and row["pid"]:
        try:
            os.kill(row["pid"], 0)
            return row
        except OSError:
            with db() as con:
                con.execute("UPDATE servers SET pid=NULL,status='STOPPED' WHERE user_id=?", (uid,))
    return row

def stop_process(uid):
    row = server_row(uid)
    if not row or not row["pid"]:
        return
    try:
        os.killpg(os.getpgid(row["pid"]), signal.SIGTERM)
        for _ in range(20):
            try:
                os.kill(row["pid"], 0)
                time.sleep(0.15)
            except OSError:
                break
        else:
            os.killpg(os.getpgid(row["pid"]), signal.SIGKILL)
    except (ProcessLookupError, PermissionError, OSError):
        pass
    with db() as con:
        con.execute("UPDATE servers SET pid=NULL,status='STOPPED' WHERE user_id=?", (uid,))

@app.route("/")
def index():
    return redirect(url_for("dashboard") if current_user() else url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if not re.fullmatch(r"[A-Za-z0-9_]{3,24}", username):
            flash("Username: 3-24 letters, numbers or underscore.")
        elif len(password) < 10:
            flash("Password must be at least 10 characters.")
        else:
            from werkzeug.security import generate_password_hash
            try:
                with db() as con:
                    cur = con.execute("INSERT INTO users(username,password_hash) VALUES(?,?)",
                                      (username, generate_password_hash(password)))
                    new_user_id = cur.lastrowid
                copy_default_files(new_user_id)
                flash("Account created. Default files have been added to your account.")
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                flash("Username already exists.")
    return render_template("auth.html", mode="register")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        from werkzeug.security import check_password_hash
        with db() as con:
            u = con.execute("SELECT * FROM users WHERE username=?",
                            (request.form.get("username", "").strip(),)).fetchone()
        if u and check_password_hash(u["password_hash"], request.form.get("password", "")):
            session.clear()
            session["uid"] = u["id"]
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.")
    return render_template("auth.html", mode="login")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/dashboard")
@login_required
def dashboard():
    u = current_user()
    # Also sync shared folders/files (for example Pb2) into accounts created earlier.
    copy_default_files(u["id"])
    row = server_row(u["id"])
    files = sorted(p.name for p in user_dir(u["id"]).iterdir() if p.is_file() and not p.is_symlink())
    folders = sorted(p.name for p in user_dir(u["id"]).iterdir() if p.is_dir() and not p.is_symlink())
    return render_template("dashboard.html", user=u, server=row, files=files, folders=folders)

@app.route("/file/<name>")
@login_required
def view_file(name):
    if not current_user()["is_admin"]:
        abort(403)
    if not valid_name(name) or not name.endswith(".py"):
        abort(404)
    p = user_dir(current_user()["id"]) / name
    if not p.is_file() or p.is_symlink():
        abort(404)
    return render_template("file.html", name=name, content=p.read_text(errors="replace")[:50000])

@app.route("/folder/create", methods=["POST"])
@login_required
def create_folder():
    name = request.form.get("name", "").strip()
    if not valid_name(name):
        flash("Folder name must use letters, numbers, dot, dash or underscore.")
    else:
        target = safe_user_path(current_user()["id"], name)
        if target.exists(): flash("That name already exists.")
        else:
            target.mkdir(parents=False)
            flash("Folder created.")
    return redirect(url_for("dashboard"))

@app.route("/folder/<path:name>")
@login_required
def open_folder(name):
    folder = safe_user_path(current_user()["id"], name)
    if not folder.is_dir() or folder.is_symlink(): abort(404)
    entries = sorted([(x.name, x.is_dir()) for x in folder.iterdir() if not x.is_symlink()])
    return render_template("folder.html", name=name, entries=entries)

@app.route("/folder/delete/<path:name>", methods=["POST"])
@login_required
def delete_folder(name):
    folder = safe_user_path(current_user()["id"], name)
    if folder.is_dir() and not folder.is_symlink():
        shutil.rmtree(folder)
        flash("Folder and its contents deleted.")
    return redirect(url_for("dashboard"))

@app.route("/zip/create", methods=["POST"])
@login_required
def create_zip():
    names = request.form.getlist("items")
    if not names:
        flash("Select at least one file or folder to ZIP.")
        return redirect(url_for("dashboard"))
    uid = current_user()["id"]
    dest = safe_user_path(uid, "project.zip")
    try:
        with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
            for name in names:
                item = safe_user_path(uid, name)
                if not item.exists() or item.is_symlink(): continue
                if item.is_file(): zf.write(item, item.relative_to(user_dir(uid)))
                else:
                    for child in item.rglob("*"):
                        if child.is_file() and not child.is_symlink(): zf.write(child, child.relative_to(user_dir(uid)))
        flash("ZIP created: project.zip")
    except Exception as e:
        flash("ZIP creation failed: " + str(e)[:120])
    return redirect(url_for("dashboard"))

@app.route("/zip/extract/<name>", methods=["POST"])
@login_required
def extract_zip(name):
    uid = current_user()["id"]
    archive = safe_user_path(uid, name)
    if not archive.is_file() or archive.suffix.lower() != ".zip" or archive.is_symlink(): abort(404)
    target = safe_user_path(uid, archive.stem + "_extracted")
    target.mkdir(exist_ok=True)
    try:
        with zipfile.ZipFile(archive) as zf:
            for member in zf.infolist():
                dest = (target / member.filename).resolve()
                if dest != target and target not in dest.parents: continue
                if member.is_dir(): dest.mkdir(parents=True, exist_ok=True)
                else:
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    with zf.open(member) as r, open(dest, "wb") as w: shutil.copyfileobj(r, w)
        flash("ZIP extracted.")
    except zipfile.BadZipFile:
        flash("Invalid ZIP file.")
    return redirect(url_for("dashboard"))

@app.route("/credentials", methods=["GET", "POST"])
@login_required
def edit_credentials():
    """Allow editing only the Uid and Pw string assignments in the user's main.py."""
    uid = current_user()["id"]
    main_file = user_dir(uid) / "main.py"
    if not main_file.is_file() or main_file.is_symlink():
        flash("আগে main.py আপলোড করুন।")
        return redirect(url_for("dashboard"))

    source = main_file.read_text(encoding="utf-8", errors="replace")
    uid_pattern = re.compile(r"(?m)^(\s*Uid\s*=\s*)(['\"])(.*?)\2(\s*(?:#.*)?)$")
    pw_pattern = re.compile(r"(?m)^(\s*Pw\s*=\s*)(['\"])(.*?)\2(\s*(?:#.*)?)$")
    uid_match = uid_pattern.search(source)
    pw_match = pw_pattern.search(source)

    if not uid_match or not pw_match or len(uid_pattern.findall(source)) != 1 or len(pw_pattern.findall(source)) != 1:
        flash("main.py-তে Uid এবং Pw-এর সঠিক একটিমাত্র assignment পাওয়া যায়নি।")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        new_uid = request.form.get("uid", "").strip()
        new_pw = request.form.get("pw", "")
        if not new_uid or len(new_uid) > 64 or any(ch in new_uid for ch in "\r\n"):
            flash("UID ১-৬৪ অক্ষরের হতে হবে।")
        elif not new_pw or len(new_pw) > 512 or any(ch in new_pw for ch in "\r\n"):
            flash("Password/Hash ১-৫১২ অক্ষরের হতে হবে এবং নতুন লাইন থাকা যাবে না।")
        else:
            updated = uid_pattern.sub(lambda m: m.group(1) + repr(new_uid) + m.group(4), source, count=1)
            updated = pw_pattern.sub(lambda m: m.group(1) + repr(new_pw) + m.group(4), updated, count=1)
            # Write atomically so a failed save cannot leave main.py half-written.
            temp_file = main_file.with_name("main.py.tmp")
            temp_file.write_text(updated, encoding="utf-8")
            temp_file.replace(main_file)
            flash("শুধু main.py-এর Uid এবং Pw আপডেট হয়েছে।")
            return redirect(url_for("dashboard"))

    # Do not render the stored password/hash into the page; user enters a new value to replace it.
    return render_template("credentials.html", current_uid=uid_match.group(3))


@app.route("/delete/<name>", methods=["POST"])
@login_required
def delete_file(name):
    if not current_user()["is_admin"]:
        abort(403)
    if not valid_name(name):
        abort(404)
    uid = current_user()["id"]
    row = server_row(uid)
    p = safe_user_path(uid, name)
    if row and row["script"] == name and row["pid"]:
        flash("Stop the running server before deleting its script.")
    elif p.is_file() and not p.is_symlink():
        p.unlink()
        flash("File deleted.")
    return redirect(url_for("dashboard"))

@app.route("/start", methods=["POST"])
@login_required
def start():
    uid = current_user()["id"]
    # Always run the account's default entry point.
    script = "main.py"
    p = user_dir(uid) / script
    if not p.is_file() or p.is_symlink():
        flash("Script not found.")
        return redirect(url_for("dashboard"))
    old = server_row(uid)
    if old and old["pid"]:
        flash("A process is already running. Stop it before starting another.")
        return redirect(url_for("dashboard"))
    log = user_dir(uid) / "console.log"
    try:
        with open(log, "ab") as out:
            proc = subprocess.Popen([sys.executable, "-u", str(p)], cwd=str(user_dir(uid)),
                stdin=subprocess.DEVNULL, stdout=out, stderr=subprocess.STDOUT,
                start_new_session=True, close_fds=True)
        with db() as con:
            con.execute("""INSERT INTO servers(user_id,pid,status,script,started_at,log_file)
                VALUES(?,?,'RUNNING',?,?,?)
                ON CONFLICT(user_id) DO UPDATE SET pid=excluded.pid,status='RUNNING',
                script=excluded.script,started_at=excluded.started_at,log_file=excluded.log_file""",
                (uid, proc.pid, script, time.time(), str(log)))
        flash("Server process started.")
    except Exception as e:
        flash("Could not start process: " + str(e)[:160])
    return redirect(url_for("dashboard"))

@app.route("/stop", methods=["POST"])
@login_required
def stop():
    stop_process(current_user()["id"])
    flash("Stop command sent.")
    return redirect(url_for("dashboard"))

@app.route("/restart", methods=["POST"])
@login_required
def restart():
    uid = current_user()["id"]
    row = server_row(uid)
    script = row["script"] if row else None
    stop_process(uid)
    if script:
        return redirect(url_for("start_from_restart", script=script))
    flash("No previous script selected.")
    return redirect(url_for("dashboard"))

@app.route("/restart/<script>", methods=["GET"])
@login_required
def start_from_restart(script):
    return redirect(url_for("dashboard"))

@app.route("/console")
@login_required
def console():
    p = user_dir(current_user()["id"]) / "console.log"
    content = p.read_text(errors="replace")[-20000:] if p.exists() else "No logs yet."
    return render_template("console.html", content=content)

@app.route("/admin")
@login_required
def admin():
    u = current_user()
    if not u["is_admin"]:
        abort(403)
    with db() as con:
        users = con.execute("SELECT id,username,is_admin,created_at FROM users ORDER BY id").fetchall()
    default_files = sorted(p.name for p in DEFAULT_FILES.iterdir()
                           if p.is_file() and not p.is_symlink() and p.suffix.lower() == ".py")
    return render_template("admin.html", users=users, default_files=default_files)

@app.route("/admin/default-files/upload", methods=["POST"])
@login_required
def admin_upload_defaults():
    if not current_user()["is_admin"]:
        abort(403)
    uploads = request.files.getlist("files")
    saved, skipped = [], []
    for f in uploads:
        name = (f.filename or "").strip()
        if not name:
            continue
        if not valid_name(name) or not name.endswith(".py"):
            skipped.append(name)
            continue
        target = DEFAULT_FILES / name
        if target.exists():
            skipped.append(name)
            continue
        f.save(target)
        saved.append(name)
    if saved:
        flash(f"Added {len(saved)} default file(s). They will be copied to new users.")
    if skipped:
        flash(f"Skipped {len(skipped)} file(s): invalid type or filename already exists.")
    if not saved and not skipped:
        flash("Choose one or more .py files first.")
    return redirect(url_for("admin"))

@app.route("/admin/default-files/delete/<name>", methods=["POST"])
@login_required
def admin_delete_default(name):
    if not current_user()["is_admin"]:
        abort(403)
    if not valid_name(name) or not name.endswith(".py"):
        abort(404)
    target = DEFAULT_FILES / name
    if target.is_file() and not target.is_symlink():
        target.unlink()
        flash("Default file deleted. Existing user copies are unchanged.")
    return redirect(url_for("admin"))

@app.route("/admin/delete/<int:uid>", methods=["POST"])
@login_required
def admin_delete(uid):
    if not current_user()["is_admin"] or uid == current_user()["id"]:
        abort(403)
    stop_process(uid)
    with db() as con:
        con.execute("DELETE FROM servers WHERE user_id=?", (uid,))
        con.execute("DELETE FROM users WHERE id=?", (uid,))
    import shutil
    shutil.rmtree(USERS / str(uid), ignore_errors=True)
    flash("User deleted.")
    return redirect(url_for("admin"))

@app.errorhandler(403)
def forbidden(_):
    return "403 - Access denied", 403

if __name__ == "__main__":
    init_db()
    # Local-only by default. Do not expose this development server to the public internet.
    app.run(host=os.environ.get("PANEL_HOST", "127.0.0.1"),
            port=int(os.environ.get("PANEL_PORT", "5000")), debug=False)
