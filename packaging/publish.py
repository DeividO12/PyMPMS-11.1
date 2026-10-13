"""
Publica en sistemasSYZ/PyMPMS-11.1 los wheels compilados de una versión.

    python packaging/publish.py --tag vX.Y.Z --wheels wheelhouse [--dry-run]

Requiere la variable de entorno SYZ_TOKEN (token con escritura en el repositorio
de SYZ) y la CLI `gh`. Pasos:

1. Verifica los wheels: 10 (Python 3.9-3.13 x Windows/Linux), de la versión del
   tag y sin código fuente (check_wheel.py).
2. Asegura que el tag exista en SYZ (el espejo lo replica, pero puede no haber
   terminado).
3. Crea el GitHub Release del tag con los wheels y las notas del CHANGELOG.
4. Agrega la carpeta vX.Y.Z/ a la rama `dist` y regenera su índice (ADR-031).
5. Descarga de vuelta cada wheel desde la rama `dist` y compara SHA-256.

Nunca reemplaza una versión ya publicada: si el Release o la carpeta existen,
falla. Un wheel puede estar ya instalado en equipos; publicar otro binario con
la misma versión dejaría dos binarios distintos bajo el mismo número.
"""

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYZ_REPO = "sistemasSYZ/PyMPMS-11.1"
DIST_BRANCH = "dist"
EXPECTED_WHEELS = 10


def run(cmd, **kw):
    print("+", " ".join(str(c) for c in cmd if "x-access-token" not in str(c)))
    return subprocess.run(cmd, check=True, text=True, **kw)


def release_notes(version: str, wheels) -> str:
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf8")
    match = re.search(rf"^## {re.escape(version)}\b.*?$(.*?)(?=^## |\Z)", changelog, re.M | re.S)
    body = match.group(1).strip() if match else "Ver CHANGELOG.md."
    names = "\n".join(f"- `{w.name}`" for w in sorted(wheels))
    return f"""{body}

## Instalación

Wheels compilados para Python 3.9–3.13 en Windows x64 y Linux x64.
Instale el que corresponda a su plataforma y versión de Python:

```bash
gh release download v{version} --repo {SYZ_REPO} --pattern "*cp312*win_amd64.whl"
pip install ./pympms_11_1-{version}-cp312-cp312-win_amd64.whl
```

O en un solo comando desde la rama `{DIST_BRANCH}`:

```bash
pip install "https://${{GH_TOKEN}}@raw.githubusercontent.com/{SYZ_REPO}/{DIST_BRANCH}/v{version}/pympms_11_1-{version}-cp312-cp312-win_amd64.whl"
```

{names}
"""


def dist_index(dist_dir: Path) -> str:
    versions = sorted(
        (d for d in dist_dir.iterdir() if d.is_dir() and re.fullmatch(r"v\d+\.\d+\.\d+", d.name)),
        key=lambda d: tuple(int(x) for x in d.name[1:].split(".")),
        reverse=True,
    )
    rows = []
    for d in versions:
        for w in sorted(d.glob("*.whl")):
            rows.append(f"| {d.name} | `{w.name}` |")
    latest = versions[0].name if versions else "vX.Y.Z"
    return f"""# Distribución de PyMPMS-11.1 (wheels compilados)

Rama generada automáticamente por `packaging/publish.py`: no editar a mano.
Cada carpeta contiene los wheels de una versión (Python 3.9–3.13, Windows x64 y Linux x64).

Instalación en un solo comando (requiere un token con lectura sobre este repositorio):

```bash
pip install "https://${{GH_TOKEN}}@raw.githubusercontent.com/{SYZ_REPO}/{DIST_BRANCH}/{latest}/<archivo.whl>"
```

| Versión | Wheel |
|---|---|
""" + "\n".join(rows) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--tag", required=True)
    parser.add_argument("--wheels", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true", help="verificar y preparar sin publicar")
    args = parser.parse_args()

    if not re.fullmatch(r"v\d+\.\d+\.\d+", args.tag):
        sys.exit(f"Tag inválido: {args.tag} (se espera vX.Y.Z)")
    version = args.tag[1:]
    token = os.environ.get("SYZ_TOKEN", "")
    if not token and not args.dry_run:
        sys.exit("Falta la variable SYZ_TOKEN (secreto SYZ_RELEASE_TOKEN del repositorio)")
    wheels = sorted(args.wheels.glob("*.whl"))

    # 1. Verificación
    run([sys.executable, str(ROOT / "packaging" / "check_wheel.py"), "contents", *map(str, wheels),
         "--version", version, "--expect", str(EXPECTED_WHEELS)])

    notes = Path(tempfile.mkdtemp()) / "notes.md"
    notes.write_text(release_notes(version, wheels), encoding="utf8")
    if args.dry_run:
        print(notes.read_text(encoding="utf8"))
        print("Dry run: no se publicó nada.")
        return 0

    remote = f"https://x-access-token:{token}@github.com/{SYZ_REPO}.git"
    env = {**os.environ, "GH_TOKEN": token}

    # 2. Tag en SYZ
    run(["git", "-C", str(ROOT), "push", remote, f"refs/tags/{args.tag}"])

    # 3. Release (falla si ya existe)
    run(["gh", "release", "create", args.tag, "--repo", SYZ_REPO, "--verify-tag",
         "--title", f"PyMPMS-11.1 {args.tag}", "--notes-file", str(notes), *map(str, wheels)], env=env)

    # 4. Rama dist con una carpeta por versión
    work = Path(tempfile.mkdtemp())
    clone = subprocess.run(["git", "clone", "--depth", "1", "--branch", DIST_BRANCH, remote, str(work)],
                           text=True, capture_output=True)
    if clone.returncode != 0:
        run(["git", "init", "-q", str(work)])
        run(["git", "-C", str(work), "checkout", "--orphan", DIST_BRANCH])
        run(["git", "-C", str(work), "remote", "add", "origin", remote])
    target = work / args.tag
    if target.exists():
        sys.exit(f"La rama {DIST_BRANCH} ya contiene {args.tag}: no se reemplaza una versión publicada")
    target.mkdir()
    for w in wheels:
        shutil.copy2(w, target / w.name)
    (work / "README.md").write_text(dist_index(work), encoding="utf8")
    run(["git", "-C", str(work), "-c", "user.name=github-actions[bot]",
         "-c", "user.email=github-actions[bot]@users.noreply.github.com", "add", "-A"])
    run(["git", "-C", str(work), "-c", "user.name=github-actions[bot]",
         "-c", "user.email=github-actions[bot]@users.noreply.github.com",
         "commit", "-q", "-m", f"dist: {args.tag}"])
    run(["git", "-C", str(work), "push", "origin", f"HEAD:refs/heads/{DIST_BRANCH}"])

    # 5. Ida y vuelta: lo publicado es byte a byte lo verificado
    for w in wheels:
        url = f"https://raw.githubusercontent.com/{SYZ_REPO}/{DIST_BRANCH}/{args.tag}/{w.name}"
        req = urllib.request.Request(url, headers={"Authorization": f"token {token}"})
        for attempt in range(12):  # raw.githubusercontent.com puede tardar en servir lo recién publicado
            try:
                with urllib.request.urlopen(req) as resp:
                    remote_sha = hashlib.sha256(resp.read()).hexdigest()
                break
            except urllib.error.HTTPError:
                if attempt == 11:
                    raise
                time.sleep(5)
        if remote_sha != hashlib.sha256(w.read_bytes()).hexdigest():
            sys.exit(f"SHA-256 distinto tras publicar {w.name}")
    print(f"{args.tag} publicado en {SYZ_REPO}: Release y rama {DIST_BRANCH} "
          f"({len(wheels)} wheels verificados)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
