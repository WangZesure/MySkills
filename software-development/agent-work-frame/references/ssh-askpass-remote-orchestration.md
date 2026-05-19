# SSH_ASKPASS Pattern for Remote Server Orchestration

When Hermes runs code on remote servers with password-only auth (no key), the terminal tool blocks interactive password prompts. This is the reliable non-interactive pattern.

## The Pattern

```bash
# 1. Write password script (one-time)
echo '#!/bin/bash\necho "PASSWORD"' > /tmp/ssh_pass.sh
chmod 755 /tmp/ssh_pass.sh

# 2. Every SSH call
SSH_ASKPASS=/tmp/ssh_pass.sh DISPLAY=dummy ssh -o StrictHostKeyChecking=no -p PORT root@HOST 'command'
```

## Why works when sshpass doesn't

- `sshpass` / `expect` are often not installed in WSL
- Hermes blocks `setsid` wrapper
- `SSH_ASKPASS` + `DISPLAY` triggers SSH's built-in askpass mechanism (originally for X11)

## File Transfer Pattern

```bash
# Small files: base64 via command line
B=$(base64 -w0 /path/to/local/file)
SSH_ASKPASS=... ssh ... "echo '$B' | base64 -d > /path/to/remote/file"

# Large files (weight npy 200KB+): base64 overflows cmd arg limit
# → train directly on server, or split into chunks
```

**SCP with SSH_ASKPASS works reliably** (unlike sshpass which may not be installed):
```python
env['SSH_ASKPASS'] = '/tmp/ssh_pass.sh'
env['DISPLAY'] = 'dummy:0'
subprocess.run(['scp', '-P', port, local_path, f'root@host:{remote_path}'], env=env)
```
This is the preferred way to upload code files — faster and more reliable than base64 encoding.

## Background Process Pitfalls

**Nohup via SSH_ASKPASS SSH often fails.** The `nohup ... &` pattern on the remote end causes the SSH session to hang waiting for output, even with `/dev/null` redirection. Timeout is common.

**Working approach**: Use `subprocess.Popen` with `stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL` to launch the SSH command without waiting:

```python
p = subprocess.Popen(
    ['ssh', '-p', port, host, 'nohup bash /tmp/script.sh &'],
    env=env, stdin=subprocess.DEVNULL,
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
)
# Don't call p.wait() — just let it run
```

Then poll progress separately with short SSH commands that read the log file.

For weights and large artifacts: regenerate on-server rather than transferring. For code files (<10KB), base64 transfer works reliably.

## Background Training

```bash
# terminal(background=true) with SSH_ASKPASS
SSH_ASKPASS=... ssh ... 'python3 -u train.py > /tmp/log 2>&1; echo EXIT:$?'
```

`-u` flag on python3 forces unbuffered stdout (otherwise Hermes process log shows empty output).

## Server Liveliness Check

Server may appear dead when overloaded (orphaned Python processes from prior training).
Before diagnosing as "server down":
1. `killall python3 2>/dev/null; sleep 2`
2. `free -m` — check memory not exhausted
3. `ps aux | grep python` — verify nothing consuming >1000% CPU

## Concurrent Connection Limit

Some course platform servers allow only 1-2 concurrent SSH sessions.
If terminal times out while a background process is running: the background process owns the connection.
Wait for notification rather than opening new SSH commands.

## Grade Submission Zip Format (ICS Platform)

For courses that expect `stu_upload/` extraction:
- Zip contains files at root (e.g., `__init__.py`, `layers_1.py`, `mnist_mlp_cpu.py`)
- Platform extracts to `stu_upload/` and runs `main_exp_*.py` from parent
- Imports in code MUST be `from stu_upload.layers_1 import ...` NOT `from layers_1 import ...`
- If imports are wrong: `ModuleNotFoundError: No module named 'layers_1'` — the zip was extracted and code found the files, but import prefix mismatch
