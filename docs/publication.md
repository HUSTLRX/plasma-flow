# Proposed publication — approval required

Prepared repository: `HUSTLRX/plasma-flow` (public).

Description/topics are in `github-metadata.json`. Release title and body are in
`release-notes-0.1.0.md`. Proposed first version: **0.1.0**, marked as a GitHub
prerelease. The remaining real-login and broader compatibility validation do not
yet justify a stable 1.0.0 claim.

Nothing in preparation creates a GitHub repository, pushes commits or tags, or
creates a release. Remotes are configured as:

- `origin`: `https://github.com/HUSTLRX/plasma-flow.git`
- `upstream`: `https://github.com/lenonk/virtual-desktop-bar.git`

After explicit approval, the intended actions are:

1. Recheck clean status, privacy audit, tests and the exact commit to publish.
2. Create the public repository without generated README/license/gitignore files.
3. Set its description and topics.
4. Push only `main` to `origin`, retaining its upstream ancestry, then set it as
   the default branch. Do not mirror upstream refs or push all historical tags.
5. Create annotated tag `v0.1.0` on the approved commit and push that tag only.
6. Create the GitHub prerelease with the prepared title/notes. Attach no local
   binaries, logs or screenshots. Check links and published contents afterwards.

A true GitHub fork relationship is not required to retain upstream Git history;
this plan creates an independent repository with attribution and an upstream
remote. No tag or release is created during local preparation.

Source hygiene applies to the current tree and all newly authored commits.
Unmodified upstream history includes original author identities and historical
upstream screenshots/IDE files. Retaining that history is intentional; publishing
it will retain those historical objects even though they are absent from the tip.
