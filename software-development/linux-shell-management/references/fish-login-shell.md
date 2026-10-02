# Fish login-shell reference

## Minimal safe procedure

1. Resolve the binary without guessing its prefix:

   ```bash
   fish_path="$(command -v fish)"
   test -n "$fish_path" && test -x "$fish_path"
   ```

2. Check that the **exact** path is present in `/etc/shells`.
3. Read the current account record:

   ```bash
   user="$(id -un)"
   getent passwd "$user"
   ```

   The login shell is the final, seventh colon-delimited field.
4. In a normal interactive terminal, run:

   ```bash
   chsh -s "$fish_path"
   ```

   Enter the account password only into that terminal if prompted.
5. Start a new login session and verify with `getent passwd "$user"`; do not
   rely only on `$SHELL` in the old session.

## Authentication boundary

An agent should not transport or type the password. If an automation channel
shows `Password:` but cannot securely accept user input, terminate that attempt
and hand the one-line command to the user for execution in a normal terminal.
A process that remains at the prompt has not completed the change, regardless
of any earlier command output.

## Reverting

Record the old shell before changing it. Revert with the same `chsh -s` command
using that exact, validated path; do not assume Bash has the same path on every
Linux distribution.

## Separation from scripts

Changing the interactive login shell to Fish does not require rewriting Bash or
POSIX scripts. Their shebang selects their interpreter independently.