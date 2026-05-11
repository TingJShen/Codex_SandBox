# 260511 Codex Tools

This directory is a snapshot of the small local tools currently managed through Codex Toolbox on the author's Windows machine.

## Included tools

- `codex_toolbox/`
  - The shared `CodexToolbox.exe` manager and its Python sources.
  - Includes the thread repair tool integration, GPU dashboard integration, COL realtime integration, and the static CatLaw report entry.
- `gpu_status_dashboard/`
  - The packaged `GPUStatusDashboard.exe`.
  - Source files for the local GPU/CPU status dashboard and the PowerShell query script it launches.
- `col_realtime_orchestration/`
  - The `colang` package files used by the realtime orchestration dashboard.
- `catlaw_pipeline_report/`
  - The static HTML pipeline comparison report and its local data script.

## Notes

- These files were copied from active working directories on `D:\Codex_Sandbox`.
- Some source files still contain absolute Windows paths that match the original local environment.
- Packaged `.exe` files are included for convenience alongside their source snapshots.

## Original source locations

- Codex Toolbox manager:
  - `D:\Codex_Sandbox\Codex_Resume`
- GPU Status Dashboard:
  - `D:\Codex_Sandbox\Huawei_Hard`
- COL realtime orchestration dashboard:
  - `D:\Codex_Sandbox\260421_Codex_Language`
- CatLaw static report:
  - `D:\Codex_Sandbox\CatLaw\Docs`
