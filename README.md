# StackQL Provider Tests

This repository contains a set of tests for StackQL providers. It is intended to be used by GitHub actions in the [stackql-provider-registry](https://github.com/stackql/stackql-provider-registry).

The registry's main packaging workflow still invokes this repository.

## Quantum-safe signed-provider checks

Use a StackQL build containing the ML-DSA migration; older binaries understand
only the retired `.sig` format. The `signed=true` mode in the existing runner
continues to select `verifyConfig.nopVerify: false`.

For a signature-specific check without virtualenv dependencies or a potentially
pre-existing, unverified server:

```sh
python verify-provider.py aws --registry-root /path/to/provider-tests \
  --stackql-bin /path/to/new/stackql
```

The root must contain `src/<provider>/<version>/provider.yaml` and service
documents. The checker runs a fresh CLI to read provider metadata and every
declared service. It fails on stderr even when StackQL reports a query failure
with exit status zero. It neither starts nor stops a shared server.
`--public-keys keys.json` supplies explicit `kid` to hex ML-DSA-65 public keys
for private registries or ephemeral test fixtures; omit it for the embedded
production keyset. Never provide private seeds.

Unsigned or sidecar-only archives must be re-signed before this check can pass.
Signature verification remains opt-in for normal StackQL usage. Archive
extraction and freshness/rollback protection are outside these checks.

Run the checker unit tests with `python -m unittest test_verify_provider`.

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