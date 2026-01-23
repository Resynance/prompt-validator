# Release Notes

All notable changes to the Prompt Similarity Detector will be documented in this file.

## [0.6.2] - 2026-01-23
### Changed
- **Maintenance**: Minor version bump and internal consistency updates.

---

## [0.6.1] - 2026-01-23
### Added
- **Automated Packaging**: Added `scripts/package.sh` to generate versioned `.tgz` release artifacts while automatically excluding development bloat.

---

## [0.6.0] - 2026-01-23
### Added
- **Possible Workflow Detection**: A new analysis layer that automatically extracts and displays a step-by-step logical breakdown of user prompts.
- **Versioning Infrastructure**: Established the baseline for application version tracking and healthy heartbeats.

### Changed
- **Terminology**: Renamed "Intended Workflow" to "**Possible Workflow**" to better reflect the nature of LLM interpretative logic.
- **UI Guide Updates**: Documentation now includes visual demonstrations of the new workflow analysis features.

### Fixed
- **Frontend Stability**: Resolved a critical syntax error in `script.js` caused by a duplicate variable declaration that was preventing UI rendering.
- **Asset Portability**: Fixed broken image links in documentation by standardizing project-relative paths.

---

## [0.5.0] - 2026-01-21
### Added
- **Mandatory Requirements**: Projects now require defined requirements to ensure analysis quality, preventing ambiguous "No Issues" results.
- **Project Focus Field**: Introduced a new optional field for granular compliance checking (e.g., "Must focus on performance" or "Use informal tone").
- **Improved Compliance Feedback**: Redesigned LLM analysis prompt and UI to provide detailed, positive summaries for satisfactory prompts.
- **System Info API**: Added `/api/info` endpoint to expose application version and health status.

### Changed
- **UX Protection**: The "Analyze Prompt" button now disables and displays an "Analyzing..." state during processing to prevent duplicate requests.
- **Documentation Overhaul**: Centralized all guide visuals into `Documentation/Media` and updated `api_docs.md` to reflect the new schema.

### Fixed
- **Database Migrations**: Implemented automatic schema updates in `db_manager.py` to handle the transition to mandatory requirements and new focus fields.
- **CLI Sync**: Updated `manage_project.py` to enforce new validation rules.
