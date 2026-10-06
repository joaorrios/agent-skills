# Sources

The official documentation is authoritative for documented behavior. Append `.md` to any page URL for a plain-markdown copy. When it disagrees with this skill, follow the documentation and note the difference to the user.

| Page | Settles |
|---|---|
| [Legal and compliance](https://code.claude.com/docs/en/legal-and-compliance) | What subscription OAuth and API keys may be used for; that sign-in must complete through Anthropic's own flow. |
| [Authentication](https://code.claude.com/docs/en/authentication) | Multiple accounts through `CLAUDE_CONFIG_DIR`; where credentials and the Keychain entry live; credential precedence; which credentials the Desktop ignores; Anthropic profiles. |
| [Manage sessions](https://code.claude.com/docs/en/sessions) | Transcript location and project directory naming; `CLAUDE_CODE_PROJECT_DIR_NAME`; resume lookup order and the duplicate-copy rule. |
| [Claude Desktop](https://code.claude.com/docs/en/desktop) | Desktop sign-in, synced skills and plugins, and resuming CLI sessions in the Desktop. |
| [The .claude directory](https://code.claude.com/docs/en/claude-directory) | What lives under the config dir, including set-aside transcript files; automatic cleanup and the separate retention for Desktop and Cowork transcripts. |
| [Settings reference](https://code.claude.com/docs/en/settings-reference) | `cleanupPeriodDays` and `desktopSessionCleanupPeriodDays`. |
| [Environment variables](https://code.claude.com/docs/en/env-vars) | Current behavior of `CLAUDE_CONFIG_DIR` and related variables. |
| [Agent SDK sessions](https://code.claude.com/docs/en/agent-sdk/sessions) | Moving a session file to another machine and resuming it; session listing and inspection APIs. |

Desktop internals (`--user-data-dir`, the `claude-code-sessions` records and their per-account partitions, the startup scan, the Desktop account following the data dir, a symlinked data dir) are undocumented. Their descriptions in this skill come from inspecting the app and can change with any release; verify them on the machine before acting.
