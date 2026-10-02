# Hermes sudo headless reference — PCL snapshot

**Last verified**: 2026-09-14

This is a reconfirmable environment note, not a substitute for live checks.
Do not assume the rule or service state remains unchanged.

## Observed context

- Unix account: `kiwel`, member of `wheel`.
- Hermes gateway: `hermes-gateway.service` active.
- Hermes profile file: `/home/kiwel/.hermes/.env`, mode `0600`; no `SUDO_PASSWORD` key was present at verification time.
- Hermes terminal backend: `terminal.backend` was not set in `config.yaml`; the documented default is `local`.
- Before the change, `sudo -n -v` required a password and only a few Omarchy commands were `NOPASSWD`.

## Applied policy

After explicit operator selection, the following rule was installed:

```sudoers
kiwel ALL=(ALL) NOPASSWD: ALL
```

Installed path and permissions:

```text
/etc/sudoers.d/99-kiwel-hermes  root:root  0440
```

A non-secret source copy remains at:

```text
/home/kiwel/.config/hermes/99-kiwel-hermes-sudoers  kiwel:kiwel  0600
```

## Verified behavior

- Privileged `visudo -c` parsed the main file and all included files successfully.
- `sudo -n true` returned success.
- `sudo -n id -u` returned `0`.
- The ordinary Hermes terminal path was exercised with `sudo id -u` returning `0` and `sudo whoami` returning `root` without a prompt.
- `sudo -n -l` showed `(ALL) NOPASSWD: ALL` in the effective policy.

## Important boundary

This policy applies to every process running as `kiwel`, not only Hermes or
Alfred. A future narrowing or removal must be treated as a deliberate policy
change; deleting the installed rule requires explicit operator authorization.

The Hermes command-approval layer remains separate from sudo authentication.
Do not disable approval prompts as an automatic consequence of this policy.

## Revalidation recipe

Run these checks on the live PCL before relying on the snapshot:

```bash
id -un
id
sudo -n true
sudo -n id -u
sudo -n -l
sudo -n visudo -c
```

If the rule is changed, verify the installed file owner/mode and exercise the
same harmless command through the actual Hermes caller (local terminal,
gateway, or delegated parent as applicable).
