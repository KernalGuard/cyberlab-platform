# Install Docker on macOS

Works on Apple Silicon (M1–M4 and later) and Intel Macs. **Status: draft. Not yet walked through by a student.**

## 1. Check which chip you have
 menu → **About This Mac**. "Chip: Apple M…" means **Apple Silicon**; "Processor: Intel…" means **Intel**.

## 2. Install Docker Desktop
1. Go to Docker's official install page for Mac: <https://docs.docker.com/desktop/setup/install/mac-install/> and check its current macOS version requirements.
2. Download the version for **your chip** (Apple Silicon or Intel).
3. Open the `.dmg` and drag **Docker** to **Applications**.
4. Open Docker from Applications. Accept the license (Docker Desktop is free for personal and educational use; your instructor will confirm the course's position).
5. Wait until Docker Desktop says it is **running**.

## 3. Give Docker enough memory
Docker Desktop → **Settings** (gear icon) → **Resources** → set **Memory** to **4 GB** → **Apply & restart**.
On an 8 GB Mac, 4 GB is the right balance. Don't go higher.

## 4. Check it works
Open **Terminal** and run:

```bash
docker version
docker compose version
docker run --rm hello-world
```

You should see version numbers for both Client and Server, and "Hello from Docker!".

## 5. Get the lab files
```bash
cd ~
git clone https://github.com/KernalGuard/cyberlab-platform.git
```
If `git` is not installed, macOS will offer to install the Command Line Tools. Accept. Or download the repository ZIP from GitHub instead.

Continue with [Lab 0](../../labs/lab0-orientation/docs/student-guide.md).

## Alternatives (not officially supported yet)
[Colima](https://github.com/abiosoft/colima) and Rancher Desktop are free alternatives to Docker Desktop. They should work, but the course has not tested them yet.
