I will implement the code for Real Docker Support and the Tauri Backend, acknowledging that runtime verification for these specific components is limited by the current environment (missing Docker/Rust). I will also upgrade the React Frontend to a functional MVP Dashboard.

## 1. Real Docker Support (Code Implementation)
*   **Update Dependencies:**
    *   Add `docker` to `apps/sidecar/requirements.txt`.
    *   Add `google-genai` to `packages/brain/Dockerfile`.
*   **Implement RealDockerClient:**
    *   Modify `apps/sidecar/core/docker_client.py` to support the `docker` Python SDK.
    *   Implement `pull_image` and `run_container` logic, including:
        *   Mounting the `packages/skills` directory (hot-reloading for skills).
        *   Setting `network_mode="host"` (Linux) or configuring `host.docker.internal` (Mac/Win) for Sidecar connectivity.
    *   Add a `USE_MOCK_DOCKER` env var toggle, defaulting to `True` if the Docker daemon is unreachable.

## 2. Tauri Backend Scaffolding (Structure)
*   **Create Rust Project Structure:** Initialize `apps/desktop/src-tauri` manually (since `cargo` is unavailable).
    *   `Cargo.toml`: Define dependencies (`tauri`, `serde`, `tauri-plugin-shell`).
    *   `tauri.conf.json`: Configure the app identifier, permissions, and Sidecar binary definition.
    *   `src/main.rs`: Implement the entry point, including:
        *   Sidecar management (launching the Python process).
        *   System tray menu.
        *   Basic commands (`greet`, `get_app_config`).

## 3. React Frontend MVP (UI/UX)
*   **Enhance Dashboard:** Update `apps/desktop/src/App.tsx` to provide a real MVP interface:
    *   **Status Panel:** Show connection status to Sidecar (mocked in browser, real in Tauri).
    *   **Task Trigger:** A button to run "Daily Brief".
    *   **Log Console:** A scrolling text area to display the JSON logs streaming from the Sidecar/Container.
*   **Browser Compatibility:** Ensure the UI gracefully handles missing Tauri APIs (using a `window.__TAURI__` check) so it can be previewed in the standard browser.

## 4. Verification
*   **Code Review:** Verify file structures and syntax.
*   **Frontend Preview:** Launch the Vite dev server (`npm run dev`) to verify the Dashboard UI and its interaction with the Mock Sidecar (via HTTP requests).
