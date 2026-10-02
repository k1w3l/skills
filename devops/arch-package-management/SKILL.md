---
name: arch-package-management
description: >-
  Use for Arch Linux package/repository/AUR management.
---

# Arch Linux package management

Manage packages on Arch-derived systems, including Omarchy, without confusing
binary repositories, third-party repositories, and the Arch User Repository
(AUR). Use this skill for package installation, `pacman`/AUR errors, package
renames, DKMS prerequisites, package-source triage, and hardware-sensitive
version pins.

## Scope

This is an operational skill for an installed Arch-derived system. It covers:

- diagnosing `target not found` and related package lookup errors;
- separating official repository packages from AUR packages;
- installing AUR packages safely with an AUR helper such as `yay`;
- selecting kernel headers for DKMS modules;
- handling renamed, split, `-bin`, `-git`, and out-of-date AUR packages;
- verifying package and DKMS state after installation; and
- preserving hardware-specific package pins instead of blindly taking the
  newest repository version.

It does not replace a hardware-specific skill or a distribution's own package
front-end. On Omarchy, consult the `omarchy` skill first for the documented
`omarchy pkg` command; use the split `pacman`/`yay` workflow below whenever the
package source, rename, or hardware pin must be explicit.

## Core model

- `pacman` searches the configured binary repositories and local sync
  databases. It does not search, build, or install an AUR PKGBUILD.
- The AUR contains user-maintained build recipes, not official binary packages.
  An AUR helper automates clone, dependency resolution, build, and installation;
  it does not make the resulting package official or inherently trusted.
- `yay` can handle both repository and AUR packages, but it must be run as the
  regular user. Do not use `sudo yay`; `yay` invokes `sudo` for the privileged
  installation phase when necessary.
- `pacman -S` validates all requested targets before committing the transaction.
  If one target is unknown, split the list and retry the valid targets instead of
  assuming that any of them were installed.

## Required workflow

### 1. Establish the package context

Before changing packages, identify the distribution, running kernel, configured
repositories, and available helpers:

```bash
cat /etc/os-release
uname -r
command -v pacman
command -v yay || command -v paru
```

For an installed package, use `pacman -Q <name>`. For a package lookup, use
`pacman -Ss <name>` for repository packages and `yay -Ss <name>` for the AUR.
Use broad searches when an exact name returns nothing; package names may have
been renamed, split, or replaced by a `-bin` or `-git` variant.

### 2. Check synchronization safely

If repository results look stale or unexpectedly empty, prefer a complete system
upgrade (`pacman -Syu`, or the distribution's documented equivalent) rather
than a standalone `pacman -Sy`, which can create a partial-upgrade state. Do not
run a full upgrade merely to answer a lookup question when the user has not
authorized that state-changing operation; report the stale-database possibility
and ask or provide the command.

### 3. Classify and normalize the requested list

For each requested name, record one of:

1. official repository package;
2. AUR package;
3. renamed/replaced package;
4. package that is present but marked out of date; or
5. package requiring a machine-specific pin or older build.

Do not silently substitute a similar package. Explain the mapping, preserve
literal identifiers in the user's request, and verify the replacement before
using it. Treat `-git` packages as moving build inputs and check their current
AUR metadata before installation.

### 4. Install in separate transactions

Install official packages with `pacman`:

```bash
sudo pacman -S --needed package-a package-b
```

Install AUR packages with the helper as the regular user:

```bash
yay -S --needed aur-package-a aur-package-b
```

Keep these groups separate when diagnosing a mixed command. Review the AUR
PKGBUILD/diff prompts and dependency changes. Never type passwords into a
script, tool argument, or chat message.

### 5. Prepare DKMS correctly

DKMS modules need the headers for the kernel that will load them. Determine the
kernel package and choose its matching header package; do not assume generic
`linux-headers` when the system runs a custom or derivative kernel. Install
`dkms` if it is not already present, then verify:

```bash
uname -r
pacman -Q dkms
pacman -Q <matching-kernel-headers>
dkms status
```

A package's build failure is not evidence that the package name is wrong: first
distinguish lookup failure, missing headers, dependency failure, and source/build
failure.

### 6. Protect hardware-specific pins

Before installing a latest package for RGB, fan control, sensors, or other
hardware, check the machine's hardware skill and runbook. A newer package can
introduce a firmware, device-layout, or shared-library regression even when the
package manager reports a valid upgrade. Keep the pin and compatibility library
explicit, and document the reason and the revalidation trigger.

## Vendor/self-extracting installers

When a requested application is not an official repository or AUR package and the vendor provides a self-extracting installer (`.run`, Makeself, or similar), do not silently substitute an unrelated package. Classify the installer separately from pacman/AUR and verify it like any other system installation.

1. Inspect the installer before executing it: use its documented `--help`, metadata, integrity-check, and file-list options; inspect the embedded install script when the archive supports it.
2. Check whether it writes system paths (`/usr/bin`, `/usr/share`, `/etc`) or installs a systemd service. If root is required, test privilege availability before starting an interactive flow.
3. Never place a password in a command, pipe, script, tool argument, or chat. If `sudo -n` reports that a password is required, stop the automated path and give the user a command to run in their own terminal.
4. If the installer creates or binds an application account/profile, run it once as the intended regular user with no account, user, or password variables preloaded. Let the installer's own prompts perform registration; pre-seeding can bind state to the wrong profile or skip account-registration hooks.
5. Pre-answer only non-secret installer prompts when the user runs the command interactively; keep service ownership, profile paths, and log paths explicit.
6. Verify the actual result: installed binaries, configuration directory, unit file, service state, and a functional endpoint or version output. A successful archive check or installer exit alone is not proof of a working installation.

For a reusable checklist, see `references/vendor-installer-triage.md`.

## Legacy shared-library dependencies for vendor installers

A vendor installer can report a misleading architecture/platform failure when its probe binary is missing an old shared library. On Arch-derived systems, first read the exact loader error instead of changing architecture or distro packages blindly.

- For `libcrypt.so.1: cannot open shared object file`, search the official repositories for the compatibility package and install it with `sudo pacman -S --needed libxcrypt-compat`.
- Verify the library path (`/usr/lib/libcrypt.so.1`) and rerun the vendor installer; do not interpret this specific error as an x86_64 mismatch.
- A legacy installer may print `service: command not found` while probing an old SysV init interface and later detect systemd successfully. If it continues, verify the generated systemd unit, `systemctl is-enabled`, `systemctl is-active`, the journal, and the advertised listener before treating the warning as fatal.

## Troubleshooting `target not found`

Use this decision sequence:

1. **Official lookup succeeds, install fails**: inspect dependencies, conflicts,
   architecture, held packages, and synchronization state.
2. **`pacman -Ss` is empty but `yay -Ss` finds it**: it is an AUR package; use
   `yay`, not `pacman`.
3. **Both exact lookups are empty**: search a shorter stem, check for a rename or
   split package, and inspect the authoritative package page. Do not invent a
   substitute.
4. **Some names resolve and some do not**: split the command. The valid names
   may not have been installed because the original transaction was rejected.
5. **AUR package is marked out of date**: prefer a maintained binary or current
   replacement only after checking that it provides the required application;
   otherwise report the risk rather than hiding it.
6. **A package is installed but the daemon fails after a system upgrade**:
   inspect the service status, journal, package changelog, and dynamic-library
   dependencies. Rebuild a source AUR package against the current libraries when
   that is the confirmed cause; do not downgrade unrelated system packages by
   reflex.

## Verification checklist

After an installation or repair, verify the exact external state:

```bash
pacman -Q package-a package-b
pacman -Qm                         # review foreign/AUR packages when relevant
dkms status                         # for DKMS hardware
systemctl status <service>          # for each enabled service
```

Use the actual service name and a non-mutating status query. For binaries that
failed to start because of shared libraries, `ldd /path/to/binary` must not
show `not found`; then check the service exit status and journal. Do not claim
success from a successful build prompt alone.

## Supporting detail

- The PCL OpenRGB rc2 restore procedure, including the `mbedtls3` rebuild, pinning,
  archive caveat, and IT5711 profile verification, is in
  [`references/openrgb-rc2-omarchy.md`](references/openrgb-rc2-omarchy.md).

## Anti-patterns

- Sending AUR names to `sudo pacman -S` and treating the resulting error as a
  network or password problem.
- Running `sudo yay`, `sudo makepkg`, or building AUR recipes from a root shell.
- Using `pacman -Sy` alone on a rolling-release system.
- Replacing a package name based only on a similar spelling without checking
  `provides`, `conflicts`, and current package metadata.
- Updating a hardware-sensitive package just because it is the newest version.
- Reporting that valid targets were installed when the mixed transaction was
  rejected and no read-back was performed.

## Completion criteria

- [ ] The distribution, kernel, and package helper were identified.
- [ ] Every target was classified using current repository/AUR lookups.
- [ ] Renames, `-bin` alternatives, out-of-date flags, and hardware pins were
      explained rather than silently changed.
- [ ] Official and AUR packages were installed in the correct user/privilege
      context.
- [ ] Matching kernel headers and DKMS prerequisites were checked.
- [ ] Installed package, service, and DKMS state were read back before claiming
      completion.
