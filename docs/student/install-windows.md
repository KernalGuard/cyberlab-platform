# Install Docker on Windows 10/11 (WSL 2)

**Status: draft. Not yet walked through on a Windows machine.** If any step differs from what you see, tell your instructor.

Docker on Windows runs Linux containers inside **WSL 2** (Windows Subsystem for Linux). You will run all lab commands inside an **Ubuntu** terminal provided by WSL.

## 1. Confirm virtualization is enabled
Task Manager → **Performance** → **CPU** → "Virtualization: **Enabled**". If disabled, enable it in your BIOS/UEFI first.

## 2. Install WSL 2 and Ubuntu
Open **PowerShell as Administrator** (right-click → Run as administrator):

```powershell
wsl --install
```

Restart when asked. After the restart an **Ubuntu** window opens. Choose a Linux username and password (they do not need to match your Windows login).

Check it worked (in PowerShell):

```powershell
wsl --list --verbose
```

Ubuntu should show **VERSION 2**.

## 3. Install Docker Desktop
1. Download Docker Desktop for Windows from <https://docs.docker.com/desktop/setup/install/windows-install/> and check its current requirements.
2. Run the installer and keep **"Use WSL 2 instead of Hyper-V"** selected.
3. Start Docker Desktop and wait until it says it is **running**.
4. Docker Desktop → **Settings** → **Resources** → **WSL integration** → turn on integration for **Ubuntu** → **Apply & restart**.

## 4. Limit memory used by WSL (recommended on 8 GB laptops)
With WSL 2, memory is controlled by WSL, not by Docker Desktop's slider. In PowerShell:

```powershell
notepad "$env:USERPROFILE\.wslconfig"
```

Put this in the file, save, and close Notepad:

```ini
[wsl2]
memory=4GB
```

Then apply it:

```powershell
wsl --shutdown
```

Start Docker Desktop again.

## 5. Check it works
Open the **Ubuntu** app (Start menu → Ubuntu) and run:

```bash
docker version
docker compose version
docker run --rm hello-world
```

## 6. Get the lab files inside WSL (important)
Clone the labs **inside your Ubuntu home folder**, not into `C:\Users\…`. This avoids Windows line-ending and file-permission problems and is much faster:

```bash
cd ~
sudo apt-get update && sudo apt-get install -y git   # if git is missing
git clone https://github.com/<course-org>/cyberlab-platform.git
```

To see these files in Windows Explorer, type `\\wsl$` in the Explorer address bar, or run `explorer.exe .` from the Ubuntu terminal.

Continue with [Lab 0](../../labs/lab0-orientation/docs/student-guide.md). **Run every lab command in the Ubuntu terminal.**
