# ScriptUI ↔ Native Bridge Protocol

The user-facing ScriptUI panel and the resident native helper communicate through two small text files.

## Location

`Folder.userData/AE Hot Loader/bridge/`

On macOS this resolves under the user's Application Support area.

## Request

File: `request.txt`

Example:

```
version=1
command=reload_plugins
request_id=1720000000000-123456
timestamp=1720000000000
```

The panel replaces the previous request atomically enough for the PoC and waits for a matching response.

## Response

File: `response.txt`

Example:

```
version=1
request_id=1720000000000-123456
status=success
message=Late registration callback returned success
```

Possible status values:
- `success`
- `error`
- `noop`

## Threading rule

The ScriptUI panel only writes files. It never calls native AE APIs.

The native helper reads the request from an AE idle hook, so host registration happens on the AE main thread.
