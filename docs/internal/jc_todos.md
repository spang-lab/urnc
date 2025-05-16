# Journal Club Todos

This document contains a list of issues, that should be solved before the journal club talk at May 20, 2025.

## Make sure that all CLI commands are documented

Every command should contain a short description of the command and its arguments as well as a link to the online documentation.

## Write testcases for the following checks

1. Check that `urnc convert -t clear` and `urnc check --clear` do the same thing (mentioned in `check.md`).

2. Check that `urnc convert -t fix INPUT` and `urnc check --fix` do the same thing (mentioned in `check.md`).

3. Check that `urnc execute INPUT` and `urnc convert -t execute INPUT` are equivalent (mentioned in `execute.md`)

4. Check that `urnc execute -o OUTPUT INPUT` and `urnc convert -t execute:OUTPUT INPUT` are equivalent (mentioned in `execute.md`)

## Write internal/usage.md

This document should contain everything I want to show live on Tuesday, including a ton of screenshots.

## Write usage.md

Copy over relevant parts from `internal/usage.md` (see issue `Write internal/usage.md`).