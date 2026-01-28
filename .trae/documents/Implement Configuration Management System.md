I will implement a layered configuration management system for the MVP.

## 1. Update MVP Plan
*   **Update `docs/MVP_计划.md`**: Add "Configuration Management" (Settings UI + Sidecar Persistence) to the Feature List and Development Plan.

## 2. Backend Implementation (Sidecar)
*   **Create `apps/sidecar/core/config.py`**:
    *   Implement a `ConfigManager` class.
    *   Persist configuration to a local JSON file (e.g., `config.json` in the sidecar root).
    *   Provide methods to `get`, `set`, and `load` configuration.
*   **Update `apps/sidecar/api/main.py`**:
    *   Add GET `/config` endpoint to retrieve current settings.
    *   Add POST `/config` endpoint to update settings.
    *   **Crucial Integration**: Modify the `run_task` endpoint to inject the stored API Keys into the `docker_client.run_container` call as environment variables.

## 3. Frontend Implementation (Desktop)
*   **Update `apps/desktop/src/App.tsx`**:
    *   Add a **Settings Panel** (toggleable visibility).
    *   Add an input field for `GOOGLE_API_KEY`.
    *   Implement "Load" (on mount) and "Save" functionality using the new Sidecar endpoints.

## 4. Verification
*   **Restart Sidecar & Frontend**: Ensure changes take effect.
*   **Test Flow**:
    1.  Open App -> Open Settings -> Enter Dummy Key -> Save.
    2.  Run "Daily Brief" Task.
    3.  Check Logs: Verify that the "GOOGLE_API_KEY not found" warning disappears and is replaced by an authentication error (or success if a valid key is used), proving the key was successfully injected into the container environment.
