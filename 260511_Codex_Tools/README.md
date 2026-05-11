# 260511 Codex Tools

This directory is a snapshot of the small local tools currently managed through Codex Toolbox on the author's Windows machine.

## Top-level layout

- `codex_toolbox/`
  - The shared `CodexToolbox.exe` manager and its Python sources.
  - This is the "big toolbox" wrapper that aggregates the smaller tools below.
- `codex_thread_repair/`
  - The standalone Codex thread repair component.
  - Includes the PowerShell GUI scripts and the Python status helper used by the toolbox.
- `gpu_status_dashboard/`
  - The standalone GPU dashboard component.
  - Includes `GPUStatusDashboard.exe`, its Python sources, tests, and icon assets.
- `col_realtime_orchestration/`
  - The standalone COL realtime orchestration dashboard sources.
- `catlaw_pipeline_report/`
  - The standalone static CatLaw pipeline HTML report and its local data script.

## Notes

- These files were copied from active working directories on `D:\Codex_Sandbox`.
- Some source files still contain absolute Windows paths that match the original local environment.
- Packaged `.exe` files are included where they existed locally.
- The toolbox manager and the standalone components are intentionally both present, so the repository does not only contain a single large wrapper app.

## Original source locations

- Codex Toolbox manager:
  - `D:\Codex_Sandbox\Codex_Resume`
- Codex thread repair component:
  - `D:\Codex_Sandbox\Codex_Resume`
- GPU Status Dashboard:
  - `D:\Codex_Sandbox\Huawei_Hard`
- COL realtime orchestration dashboard:
  - `D:\Codex_Sandbox\260421_Codex_Language`
- CatLaw static report:
  - `D:\Codex_Sandbox\CatLaw\Docs`
