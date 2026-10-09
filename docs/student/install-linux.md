# Install Docker on Linux

**Status: draft.** The commands below were exercised on Ubuntu 24.04 x86-64 on 2026-10-09.

## 1. Install Docker Engine and the Compose plugin
Follow Docker's official instructions for your distribution: <https://docs.docker.com/engine/install/>. Install the packages `docker-ce`, `docker-ce-cli`, `containerd.io`, `docker-buildx-plugin` and **`docker-compose-plugin`**.

(Docker Desktop for Linux is also an option and behaves like the macOS version.)

## 2. Decide how you will run Docker
- **Recommended for this course:** add yourself to the `docker` group so you don't need `sudo`:
  ```bash
  sudo usermod -aG docker "$USER"   # then log out and back in
  ```
  ⚠️ Membership of the `docker` group is **equivalent to root access** on your computer. Only do this on a computer you own. **Rootless Docker** (<https://docs.docker.com/engine/security/rootless/>) avoids that risk and also works for these labs.

## 3. Check it works
```bash
docker version
docker compose version
docker run --rm hello-world
```

## 4. Make your work folder writable from the container
Lab containers run as user ID **1000**. Check yours:

```bash
id -u
```

If it is **not** 1000, tell the labs to use your IDs. Run this in each terminal before using `docker compose`, or add it to `~/.bashrc`:

```bash
export CYBERLAB_UID=$(id -u) CYBERLAB_GID=$(id -g)
```

## 5. Firewall note
Docker can bypass host firewalls such as `ufw` for **published** ports. The CyberLab analysis labs publish no ports, and later labs bind only to `127.0.0.1` (your own computer). Don't change those settings.

## 6. Get the lab files
```bash
cd ~
git clone https://github.com/<course-org>/cyberlab-platform.git
```

Continue with [Lab 0](../../labs/lab0-orientation/docs/student-guide.md).
