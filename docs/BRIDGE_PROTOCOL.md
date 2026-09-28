# ScriptUI ↔ Native Agent Protocol

The ScriptUI panel and resident `AEHotLoaderAgent.plugin` communicate through two small text files.

## Location

`Folder.userData/AE Hot Loader/bridge/`

On macOS this resolves under the user's Application Support directory.

## Request

File: `request.txt`

```
version=1
command=reload_plugins
request_id=1720000000000-123456
timestamp=1720000000000
```

For production, `reload_plugins` means:

**scan the configured Adobe plug-in roots and late-register newly installed
ordinary native effect bundles in the running AE process.**

The current implementation uses the AE 25.6 arm64 private loader followed by
the host's post-load filter-registration notification.

## Response

File: `response.txt`

```
version=1
request_id=1720000000000-123456
status=success
message=ordinary-discovery-v1: scanned=2 loaded=1 post_load_modules=1
```

Status values:
- `success`
- `error`
- `noop`

## Threading

ScriptUI only reads/writes files.

The native Agent receives the request from AE's resident AEGP path and invokes
ordinary-plugin discovery from inside the AE process.

The legacy shell implementation remains available as a separate native
component, but this command's production path performs ordinary-plugin
discovery and filter registration.
