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

**reload the implementation dylib of every loaded AE Hot Loader shell.**

It no longer means “register arbitrary new effect bundles through the private AE loader”.

## Response

File: `response.txt`

```
version=1
request_id=1720000000000-123456
status=success
message=Reloaded 2 shell implementation(s); 1 unchanged
```

Status values:
- `success`
- `error`
- `noop`

## Threading

ScriptUI only reads/writes files.

The native Agent receives the request from AE's resident AEGP path and invokes shell reload entry points from inside the AE process.

Each shell performs an atomic implementation-pointer swap. Old implementation dylibs remain loaded until AE exits.
