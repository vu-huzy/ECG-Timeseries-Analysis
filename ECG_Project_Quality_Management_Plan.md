# PROJECT QUALITY MANAGEMENT PLAN

**Project:** ECG Time Series Analysis and Static Web Demo  
**Reference schedule:** `ECG_Project_Revised.xml` (M0-M7; M7 is proposed report readiness)  
**Approach:** Parallel research, model evaluation, and an iterative static demo  
**Version:** Revised 30 October 2026  
**Status:** Proposed quality plan; M6 internal acceptance has not been recorded

> **Evidence rule:** A file or commit proves that an artifact exists; it does not prove that a quality test passed or that a proposed owner personally completed the work. Targets below are acceptance criteria, not measured results. This educational demo replays recorded MIT-BIH ECG and precomputed model outputs; it is not a live monitor or a medical device.

## 1. Purpose and actual scope

This plan defines quality assurance (preventing errors), quality control (checking the delivered artifacts), defect handling, and acceptance for the repository `ECG-Timeseries-Analysis`. It covers:

- MIT-BIH exploration, signal preprocessing, HR/RR and HRV analysis, ARIMA/SARIMA forecasting, Normal/Abnormal classification, CNN, and ST-MEM notebooks.
- The committed **static** demo: `demo/index.html` with seven analysis sections and `demo/monitor.html` with a 9-second ECG replay, past-only HR/RR trends, rule-based flags, and precomputed ST-MEM scores shown after each window completes.
- The committed generated JavaScript data, local Plotly bundle, saved ST-MEM weights/results, documentation, and handoff instructions.

The demo is viewed in a browser and can be served from a local HTTP server. Its current user flow is **choose a section or a recorded ECG sample -> inspect charts/results -> open the monitor -> select a record and control replay**. It has no ECG upload workflow, FastAPI service, Streamlit frontend, prediction endpoint, report export, or production deployment. Those items from the earlier Waterfall plan are outside this release and have no acceptance tests here.

Viewing the committed demo is separate from rebuilding data. Viewing requires the browser and the files in `demo/`; rebuilding data uses Python dependencies and may download MIT-BIH records. Re-scoring ST-MEM additionally requires the official pretrained encoder, which is not committed to this repository. Quality claims must state which of these paths was tested.

## 2. Quality evidence and known limitations

| Item                                   | Evidence available in the repository                                                                                        | Quality interpretation                                                                                                                                        |
| -------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Research notebooks                     | `notebooks/01_explore_data.ipynb`, `02_EDA.ipynb`, `03_preprocessing_data.ipynb`, ARIMA/SARIMA and classification notebooks | Methods and saved outputs exist; reproducibility still needs a controlled rerun.                                                                              |
| Static pages                           | `demo/index.html`, `demo/monitor.html`, `demo/app.js`, `demo/monitor.js`                                                    | The implementation exists; browser behavior, layout, and accessibility need execution checks.                                                                 |
| Offline viewing assets                 | `demo/data/*.js` and `demo/vendor/plotly-cartesian-2.35.2.min.js`                                                           | Data and plotting code are committed, so the viewing path is designed to work without network access.                                                         |
| ST-MEM rerun                           | `demo/results/stmem_results.json` and `demo/models/stmem_semi_finetune.pt`                                                  | The committed test record reports accuracy **0.7065**, F1 **0.7777**, and AUC **0.8165**. These are recorded model results, not a new QA run under this plan. |
| Research report comparison             | `Final_Report_TS-3.pdf`, Table 5.3, and `README.md`                                                                         | The report gives ST-MEM F1 **0.9695**. The difference from the committed rerun remains unexplained and must be disclosed.                                     |
| Displayed feature/CNN/forecast numbers | `demo/notebook_results.py`, report Tables 5.1-5.2, and ARIMA/SARIMA notebook                                                | Each displayed number needs a source check; the later sliding-window notebook does not reproduce every report value.                                          |

The October 29, 2026 commits establish that the demo and model artifacts were added. They do not establish that the checks in this document were run. The final review and internal acceptance scheduled for **October 30, 2026 (M6)** remain proposed until a test record and sign-off exist.

## 3. Proposed quality responsibilities

These are responsibility assignments for the six-person plan. They are **not claims of historical Git authorship**. Among these six names, Git directly identifies commits by Vu Quoc Huy and Tran Tuan Anh. Some notebook commits belong to `hoang3003` / Minh Hoang Tran, who is a different person from Hoang Thi Ngoc Han.

| Member                          | Proposed responsibility                                                                                   | Review evidence                                    |
| ------------------------------- | --------------------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| **Nguyen Tuan Anh (Team Lead)** | Own quality decisions, track defects and exceptions, coordinate report review, record the M6 decision.    | Signed checklist and open-defect list.             |
| **Vu Quoc Huy**                 | Check ST-MEM artifact/results, static demo integration, model limitations, and local launch instructions. | Model-result comparison and demo smoke-test notes. |
| **Tran Tuan Anh**               | Check ECG exploration, EDA, record/lead labels, and waveform interpretation.                              | Data and chart review notes.                       |
| **Nguyen Quang Huy**            | Check generated data, preprocessing descriptions, layout at agreed viewports, and offline assets.         | Data-source and browser checklist.                 |
| **Hoang Thi Ngoc Han**          | Check ARIMA/SARIMA values, feature-model tables, references, and documentation clarity.                   | Number-to-source mapping.                          |
| **Mai Tuan Manh**               | Check CNN results, monitor controls, regression scenarios, and defect retests.                            | Monitor test log and retest results.               |

Each check has one named owner and one reviewer where practical. A reviewer must not mark their own unexecuted test as passed. If an assigned member did not perform a task, the team lead should update the record rather than treating this plan as proof of contribution.

## 4. Objectives and proposed acceptance criteria

The six quality dimensions from the original plan are retained, with measures changed to fit the delivered static demo. Thresholds in this table are **proposed**; no threshold is reported as achieved here.

| Dimension       | Measure and proposed target                                                                                                                                                                                                         | Verification                                                                             | Lead                            |
| --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- | ------------------------------- |
| **Reliability** | Both pages load with all committed assets; no blocking JavaScript error or broken core control in the approved browser/record matrix. A full 306-second excerpt reaches its final completed window, stops cleanly, and restarts when Play is pressed. | Browser console/network log and timed replay checklist.                                  | Mai Tuan Manh, Vu Quoc Huy      |
| **Usability**   | In a five-person pilot, at least four can find the seven sections, open the monitor, select a record, and pause/resume playback without help. No unresolved blocker affects this path.                                              | Scripted observation; record success and assistance for each participant.                | Nguyen Tuan Anh, Tran Tuan Anh  |
| **Performance** | On the agreed local machine and browser, each page reaches a usable state within 5 seconds in at least 19 of 20 reloads; the monitor remains responsive through one full excerpt and a replay restart. | Record hardware, browser, cache policy, 20 load times per page, and replay observations. | Nguyen Quang Huy, Vu Quoc Huy   |
| **Response**    | Play/pause, speed, and record changes show a visible state change within 0.5 seconds in 20 sampled actions; an unavailable data file produces an understandable failure rather than a blank page.                                   | Timed interaction and missing-asset checks.                                              | Mai Tuan Manh                   |
| **Conformance** | All seven analysis sections and the monitor match the documented scope. Every sampled chart/table metric traces to the correct report, notebook, or committed JSON; no live-monitoring, upload, or medical-diagnosis claim is made. | Source-to-display checklist and language review.                                         | Hoang Thi Ngoc Han, Vu Quoc Huy |
| **Aesthetics**  | No clipped essential controls, unreadable labels, or overlapping charts at **1366 x 768** and **390 x 844** viewports. Keyboard focus and the monitor's labeled controls remain visible.                                            | Screenshots and keyboard walk-through in Chrome and Edge.                                | Nguyen Quang Huy, Tran Tuan Anh |

The performance and response thresholds apply only to the recorded test setup. Record failures and actual measurements before accepting or revising a target. A five-person usability pilot is a small academic check, not population-level evidence.

## 5. Assurance and control by workstream

### 5.1 Data, signals, and forecasting

- **Assurance:** Identify the MIT-BIH record, lead, sample rate, filter settings, RR/HR derivation, stationarity test, and forecast metric before a plot or number is added to the demo.
- **Control:** For at least one selected record, compare the demo's raw/processed waveform labels and HR/RR descriptions with the corresponding notebook outputs. Check units on axes and whether a chart shows a recorded signal, a calculated feature, or a forecast.
- **Pass rule:** No mislabeled record, lead, unit, or forecast source in the selected fixtures. Any notebook that depends on a local path or network download has that dependency documented.

### 5.2 Classification and ST-MEM

- **Assurance:** Keep the label rule, window length, data split, model name, metric definition, and source document with each result. Do not merge values from incompatible labeling or evaluation setups into one unqualified comparison.
- **Control:** Check feature-model and CNN values against report Tables 5.1-5.2 and the source map in `demo/notebook_results.py`. Check the committed ST-MEM test metrics against `demo/results/stmem_results.json` to four decimal places. Inspect one Normal and one Abnormal example for correct presentation.
- **Pass rule:** The display identifies the source of each compared result. The ST-MEM rerun F1 **0.7777** and report F1 **0.9695** appear as distinct results with the discrepancy stated. If `demo/predict_stmem.py` is run, record the external encoder version, environment, command, and observed metrics; this optional rerun is not required to view the committed static demo.

### 5.3 Static web demo and monitor

- **Assurance:** Keep `demo/data/*.js` and the local Plotly bundle in the release package. Maintain clear labels that the monitor replays MIT-BIH data; reveal precomputed ST-MEM scores only after their windows complete.
- **Control:** Open `index.html` and `monitor.html` using the documented local-server command. Check seven navigation sections, internal links, theme control, record selection, play/pause, speed, optional beep, 9-second sweep, HR/RR trends, illustrative flags, and return navigation. At the start, midpoint, and end of a replay, confirm that no future HR/RR sample or ST-MEM window score is visible; the final completed window remains visible when playback stops. Confirm that RR short-long is not called a confirmed PVC, a long RR is not presented as an immediate cardiac-arrest alert, rolling RMSSD is described as RR variability, and ST-MEM scores are identified as precomputed and uncalibrated. Repeat with network access disabled after the files are already present.
- **Pass rule:** No missing asset, blocking console error, frozen replay, or misleading real-time/clinical claim in the agreed test matrix. A disabled or unsupported browser feature must fail gracefully or be documented.

### 5.4 Documentation and presentation

- **Assurance:** Keep launch, rebuild, model-verification, and limitation instructions separate so a reviewer knows which path requires Python, network access, or the external pretrained encoder.
- **Control:** Have one member other than the writer follow the README viewing steps on a clean clone. Check page text and report figures for source labels and caveats.
- **Pass rule:** The reviewer can open both pages from committed assets; the handoff explains the ST-MEM metric gap and the nonmedical, replay-only nature of the demo.

## 6. Quality gates aligned with the revised schedule

Milestones M0-M5 are historical or estimated planning markers in `ECG_Project_Revised.xml`, **not retrospective quality approvals**. Research and classification activities overlap; milestone numbering does not impose Waterfall sequencing.

The schedule now places a **four-hour morning review** (08:00-12:00) before each M0-M7 gate and links it finish-to-start to a **four-hour afternoon decision** (13:00-17:00). Each review allocates 1.6 hours to the lead and 1.6 hours to a second reviewer at 40% units (3.2 hours per gate; 25.6 hours overall). Each gate is explicitly marked as a milestone with 1.6 hours of lead work at 40% units (12.8 hours overall), so it no longer appears under Unassigned in Resource Usage. All eight reviews and formal gate decisions remain **0% complete** because approval records were not supplied. Earlier M0-M5 artifact delivery remains documented separately from formal gate approval.

| Gate                                         | Schedule date           | Required quality record                                                     | Current evidence status                                              |
| -------------------------------------------- | ----------------------- | --------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| **M0 - Project scope agreed**                | 18 Mar 2026 (estimated) | Scope and responsibilities documented.                                      | Date estimated; approval record not provided.                        |
| **M1 - Exploration and preprocessing ready** | 1 Apr 2026 (estimated)  | MIT-BIH source, record/lead checks, preprocessing description.              | Notebooks exist; gate check not provided.                            |
| **M3 - Classification results available**    | 12 May 2026             | Metric source map and model limitations.                                    | Commits exist; gate check not provided.                              |
| **M2 - Forecast analysis complete**          | 14 May 2026             | ARIMA/SARIMA result and source check.                                       | Rerun commit exists; gate check not provided.                        |
| **M4 - May research report complete**        | 15 May 2026 (estimated) | Report review and outstanding discrepancy list.                             | PDF is dated May; exact completion day unverified.                   |
| **M5 - Demo and model artifacts committed**  | 29 Oct 2026             | Asset inventory and reproducibility instructions.                           | Repository commits exist; browser QA not established by the commits. |
| **M6 - Internal acceptance**                 | 30 Oct 2026 (proposed)  | Executed test log, defect disposition, limitations, and team-lead decision. | Pending; record 0% until completed.                                  |
| **M7 - Management report ready**             | 6 Nov 2026 (proposed)  | Reviewed English report, source cross-check, and consolidated schedule export. | Pending; readiness milestone, not proof of external submission.       |

## 7. Minimum test record for M6

Every row needs an actual date, environment, evidence link or screenshot, result, defect ID if failed, and reviewer. The **planned** status below must only change after the check is executed.

| ID  | Check                                                                                                                       | Evidence to retain                                  | Owner                              | Status  |
| --- | --------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------- | ---------------------------------- | ------- |
| Q01 | Load both pages locally in Chrome and Edge; verify no missing committed asset or blocking console error.                    | Browser/network log and screenshots.                | Vu Quoc Huy                        | Planned |
| Q02 | Visit all seven sections; verify links, labels, charts, and source notes.                                                   | Section checklist and discrepancies.                | Nguyen Quang Huy                   | Planned |
| Q03 | Run two records; check play/pause, speed, beep, 9-second sweep, past-only HR/RR, completed-window ST-MEM, final-window stop, and replay restart. | Control checklist and full-excerpt observation log. | Mai Tuan Manh | Planned |
| Q04 | Cross-check selected ECG, HR/RR, forecast, feature-model, CNN, and ST-MEM values with their stated sources.                 | Source-to-display matrix.                           | Tran Tuan Anh / Hoang Thi Ngoc Han | Planned |
| Q05 | Confirm report-vs-rerun ST-MEM discrepancy and replay-only/nonmedical caveats are visible in documentation or presentation. | Screenshots and handoff notes.                      | Vu Quoc Huy                        | Planned |
| Q06 | Check layout at both viewports, keyboard access to primary controls, and readable labels.                                   | Screenshots and keyboard checklist.                 | Nguyen Quang Huy                   | Planned |
| Q07 | Measure the proposed load and interaction targets on a named machine/browser; record raw timings.                           | Timing sheet with 20 loads per page and 20 actions. | Mai Tuan Manh                      | Planned |
| Q08 | Follow the README viewing path from a clean clone with no rebuild.                                                          | Command log and reviewer notes.                     | Nguyen Tuan Anh                    | Planned |

The optional Python data rebuild and optional ST-MEM model re-score may be run as separate reproducibility checks. Record them as **not run**, **passed**, or **failed**; do not mark the browser-only release as failed merely because the external encoder is unavailable.

## 8. Defect management and corrective action

| Severity          | Meaning in this release                                                                   | Example                                                                            | Disposition before M6                          |
| ----------------- | ----------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- | ---------------------------------------------- |
| **S1 - Critical** | A materially false clinical or model claim, or a result mapped to the wrong source/label. | A replay is described as live monitoring; Normal/Abnormal labels are reversed.     | Block acceptance, correct, and retest.         |
| **S2 - High**     | A core page or monitor path cannot be used.                                               | `monitor.html` fails to load, replay freezes, or a required data asset is missing. | Block acceptance, correct, and retest.         |
| **S3 - Medium**   | A significant but nonblocking presentation or reproducibility problem.                    | A chart source note is missing, or a secondary plot clips at one viewport.         | Fix or document a specific accepted exception. |
| **S4 - Low**      | Cosmetic issue with no effect on interpretation or core use.                              | Minor spacing difference.                                                          | Track for later polish.                        |

A defect record contains ID, affected page/artifact, environment, steps, expected/actual behavior, severity, owner, fix reference, and retest outcome. The team lead records any S3/S4 exception and its impact. No exception may waive an S1/S2 defect or hide the ST-MEM discrepancy.

## 9. Measurement, reporting, and acceptance decision

For each quality metric, report the **target, observed value, test setup, sample size, date, pass/fail, and evidence**. Keep raw timings and screenshots so another member can review the decision. Calculate:

- **Usability completion:** participants finishing the scripted path without help / all pilot participants.
- **Page readiness:** elapsed time from local navigation to visible, usable content; report all 20 observations for each page and the number meeting the 5-second target.
- **Control response:** elapsed time from interaction to visible state change; report all 20 observations and the number meeting 0.5 seconds.
- **Source agreement:** checked display values matching their declared source / all checked values; record numerical tolerance when a value is rounded.
- **Test completion:** executed required checks / eight required checks. An unexecuted check is **not** a pass.

**M6 passes only if:** all eight required checks are executed and pass (or an S3/S4 exception is documented), no S1/S2 defect remains open, the ST-MEM discrepancy and demo limitations are explicitly disclosed, and Nguyen Tuan Anh records the decision. If a target is missed, report the actual result and the chosen correction or exception; do not rewrite the target after the fact without recording the change.

## 10. Source basis

- `ECG_Project_Revised.xml` and `ECG_Project_Revised_Tasks.csv`: six-person responsibility plan and M0-M7 schedule with 222.4 planned assignment hours. All eight gate reviews, formal M0-M7 decisions, and M7 report tasks are proposed and remain 0%; the VND 50,000/hour rate is illustrative.
- `ECG-Timeseries-Analysis/README.md`: delivered demo scope, viewing/rebuild instructions, and known ST-MEM discrepancy.
- `ECG-Timeseries-Analysis/demo/notebook_results.py`, `demo/results/stmem_results.json`, and `Final_Report_TS-3.pdf`: sources for displayed model results.
- Git history through the three October 29, 2026 demo/model commits: evidence of committed artifacts, not of completed quality testing.

The original Waterfall quality document was used only as a source to revise. Its instructions and proposed API/upload targets do not override the current project scope or the user's six-person schedule.
