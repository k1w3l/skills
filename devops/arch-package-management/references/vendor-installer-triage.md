# Vendor self-extracting installer triage

Use this reference when software is distributed as a `.run`, Makeself archive, or another vendor installer rather than a pacman/AUR package.

## Safe preflight

1. Confirm that the requested name is not an official repository package, AUR package, or documented replacement.
2. Use the installer's own inspection options before execution, typically `--help`, metadata/info, integrity checking, and file listing. Do not assume an archive named after an application is a normal package.
3. Identify whether it writes `/usr/bin`, `/usr/share`, `/etc`, init/systemd units, or user-owned paths. This determines whether root privileges are required.
4. If root is needed, test non-interactive availability with `sudo -n true`. A password prompt is a handoff boundary: never put the password in a script, pipe, tool argument, environment value, or chat.

## Interactive handoff

When `sudo -n` fails, provide a complete command for the user to run in their own terminal. It may pre-answer non-secret installer choices, but it must leave password entry to the user and must not claim success until the installation is read back.

Keep these values explicit when the installer asks:

- binary installation path;
- resource/configuration path;
- service user;
- log path;
- whether optional cloud/account setup is enabled.

Do not enable optional account or cloud setup merely to make an installer finish; it may require credentials or create an external account configuration.

## Verification after installation

Verify all layers relevant to the application:

```bash
command -v <binary>
<binary> --version
systemctl show <service> -p ActiveState -p SubState -p UnitFileState -p Result
journalctl -u <service> -n 50 --no-pager
```

For a local HTTP service, probe its documented health or root endpoint. For a daemon that writes a global profile, confirm the profile directory and unit environment point to the intended paths. An archive integrity result or a successful installer prompt is not sufficient evidence.

## Exec failures after bootstrap

If systemd reports `203/EXEC` or `Exec format error`:

1. Read the service journal and inspect the exact `ExecStart` path.
2. Check the executable type, mode, shebang/interpreter, and interpreter target.
3. Treat a zero-byte interpreter or launcher as a corrupt environment, not as an application-level bug.
4. Preserve the broken environment by moving it to a uniquely named `.bak` path rather than deleting it; rebuild the virtual environment with `python3 -m venv`, install dependencies inside that environment, restart the service, and verify its endpoint.
5. If `systemctl enable` is blocked by regular empty placeholder files in a `.wants/` directory, preserve those files in a separate backup directory, reload systemd, enable the unit, and verify that systemd created real symlinks.

This repair pattern is safer than deleting unknown state and generalizes to user-level services whose launcher files were damaged during a restore.
