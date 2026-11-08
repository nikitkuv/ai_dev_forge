## ADDED Requirements

### Requirement: Scoped commits refuse unrelated staged work without mutation

Before staging an authorized automatic commit, the helper SHALL inspect the Git index and refuse unrelated staged paths, preserving HEAD, index, and working files. It SHALL report the offending paths and SHALL NOT unstage user work. Successful commits SHALL contain only scoped changes, including paths with spaces or non-ASCII characters. Git read failures SHALL prevent mutation.

#### Scenario: Unrelated staged modification
- **WHEN** a file outside the accepted TASK scope is already staged
- **THEN** the helper refuses before staging or committing and the unrelated staged content remains intact

#### Scenario: Unrelated staged rename
- **WHEN** an unrelated rename is staged
- **THEN** both rename endpoints are considered and the helper refuses without modifying the index

### Requirement: Scoped commits recognize tracked deletions

An absent scoped path SHALL be permitted when tracked in the index or HEAD, including an already staged deletion. An absent path unknown to both SHALL be rejected before mutation. Existing manual-policy and DONE/authorization requirements SHALL continue to apply.

#### Scenario: Accepted deletion is committed
- **WHEN** an accepted TASK deletes a tracked file and includes that path in its scope
- **THEN** the automatic commit records its deletion whether staged already or not

#### Scenario: Misspelled absent path is refused
- **WHEN** a scoped absent path is tracked in neither the index nor HEAD
- **THEN** the helper rejects that path without staging or committing
