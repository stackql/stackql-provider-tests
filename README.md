# StackQL Provider Tests

This repository contains a set of tests for StackQL providers. It is intended to be used by GitHub actions in the [stackql-provider-registry](https://github.com/stackql/stackql-provider-registry).  

## Usage

```bash
test-provider.sh <provider_name> [<provider_path> <test_for_anonymous_cols>]
```

## Example

```bash
# test a local sumologic provider from the current directory
sh test-provider.sh sumologic
```

```bash
# test a local aws provider from another directory
sh test-provider.sh aws /mnt/c/Users/javen/Documents/LocalGitRepos/stackql/local-registry
```

```bash
# test a local azure provider from the current directory with anonymous column checks
sh test-provider.sh azure . true
```