# StackQL Provider Tests

This repository contains a set of tests for StackQL providers. It is intended to be used by GitHub actions in the [stackql-provider-registry](https://github.com/stackql/stackql-provider-registry).  

## Usage

```bash
test-provider.sh <provider_name> [<signed> <provider_path> <test_for_anonymous_cols>]
```

- `provider_name` - the name of the provider to test
- `signed` - whether the provider is signed or not (default: false)
- `provider_path` - the path to the provider (default: .)
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
# test a local aws unsigned provider from another directory
sh test-provider.sh \
aws \
false \
/mnt/c/Users/javen/Documents/LocalGitRepos/stackql/local-registry
```


```bash
# test a local azure unsigned provider from the current directory with anonymous column checks
sh test-provider.sh \
azure \
false \
. \
true
```