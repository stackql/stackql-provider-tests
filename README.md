# StackQL Provider Tests

This repository contains a set of tests for StackQL providers. It is intended to be used by GitHub actions in the [stackql-provider-registry](https://github.com/stackql/stackql-provider-registry).  

## Usage

```bash
test-provider.sh <provider_name> [<signed> <provider_path> <show_columns> <test_for_anonymous_cols>]
```

- `provider_name` - the name of the provider to test
- `signed` - whether the provider is signed or not (default: false)
- `provider_path` - the path to the provider (default: .)
- `show_columns` - whether to show columns in output (default: false)
- `test_for_anonymous_cols` - whether to test for anonymous columns (default: false)

## Example

```bash
# test a local sumologic unsigned provider from the current directory
sh test-provider.sh \
sumologic
false
```

```bash
# test a local aws signed provider from another directory
sh test-provider.sh \
aws \
true \
/mnt/c/Users/javen/Documents/LocalGitRepos/stackql/local-registry
```

```bash
# test a local google unsigned provider from another directory showing columns
sh test-provider.sh \
google \
false \
/mnt/c/Users/javen/Documents/LocalGitRepos/stackql/local-registry \
true
```

```bash
# test a local azure unsigned provider from the current directory showing columns
sh test-provider.sh \
azure \
false \
. \
true
```