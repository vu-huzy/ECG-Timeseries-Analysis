# ECG Project Quality Management Plan

**Revised:** 13 Nov 2026. **Baseline period:** 27 working days, 01 Oct–06 Nov 2026. This plan uses the same 16 WBS packages, five integrated review gates, and six named members as the WBS and project management report. The checks below define required criteria and evidence; they are not claims that tests have already passed.

## 1. Quality objectives

The deliverable is research documentation and a learning demo based on recorded MIT-BIH ECG. It must stay within scope, open from the release package, make metrics traceable, and avoid suggesting live medical monitoring or alerting. Model metrics must identify their labels, splits, and experiment configurations. The ST-MEM F1 in the research report (0.9695) and the rerun result (0.7777) remain separate results until the difference is explained.

## 2. Responsibilities and timing

| Member (role) | Quality responsibility | Relevant workdays |
|---|---|---:|
| Trần Tuấn Anh (DATA) | Check MIT-BIH source, leads, labels, signal processing, and split rules. | 4–9, 23–25 |
| Vũ Quốc Huy (ML) | Check HR series, ARIMA/SARIMA parameters, metrics, and feature-model comparison conditions. | 10–13, 19–25 |
| Nguyễn Quang Huy (DL) | Check CNN/ST-MEM splits, configurations, and result files; support reconciliation of displayed scores. | 10–22, 23–25 |
| Mai Tuấn Mạnh (WEB) | Self-check both pages and their data sources before QA handover. | 14–22 |
| Hoàng Thị Ngọc Hân (QA) | Lead criteria, independent tests, defect logging, and retests; own package 5.1. | 1–9, 14–25 |
| Nguyễn Tuấn Anh (PM) | Agree scope and criteria, handle exceptions, and decide internal acceptance. | 1–3, 21–27 |

QA tests independently of the package developer. The package owner supplies data, fixes defects, and provides evidence. The PM makes the acceptance decision after reviewing the test record and does not mark tests as passed on QA's behalf.

## 3. Acceptance criteria matrix

| ID | WBS packages | Criterion and verification | Minimum evidence |
|---|---|---|---|
| QC1 | 2.1–2.2 | Record, lead, and label inventory matches the source; filtering, normalization, windows, and splits are reproducible. | Notebooks, specification, and sample reconciliation. |
| QC2 | 3.1 | Forecast plots identify record, horizon, parameters, and MAE/RMSE from the correct run. | Results table linked to notebook. |
| QC3 | 3.2–3.4 | ML/CNN/ST-MEM tables state label, split, and threshold rules; non-equivalent experiments are not ranked directly. | Metric-to-source table and limitations. |
| QC4 | 4.1–4.2 | Dashboard opens with seven sections; data and charts have labels and sources. | Chrome/Edge checklist and screenshots. |
| QC5 | 4.3 | HR/RR reveals only played samples; ST-MEM appears after each completed nine-second window; flags are identified as illustrative. | Interaction record and timestamp checks. |
| QC6 | 4.1–4.4 | Release opens offline with local JavaScript data and charting library; viewing does not require retraining. | Clean-copy test record and README. |
| QC7 | 5.1–5.2 | Report, WBS, CSV, and XML agree on 16 packages, 27 workdays, 240 hours, six members, and five integrated reviews. | Version reconciliation and arithmetic check. |
| QC8 | 5.1–5.3 | No blocking demo defects remain; remaining defects have severity, owner, and acceptance decision. | Defect log, retest results, and acceptance record. |

## 4. Quality control and review gates

| Gate | End of workday | Package | Exit condition |
|---|---:|---|---|
| M1 | 3 | 1.3 | Scope, quality criteria, and reviewers are defined. |
| M2 | 9 | 2.2 | Data, labels, and splits are stable for experiments. |
| M3 | 20 | 3.4 | Metrics have sources and limitations; major differences are recorded separately. |
| M4 | 22 | 4.3–4.4 | Both pages, offline assets, and README are ready for QA. |
| M5 | 27 | 5.3 | QC1–QC8 are reviewed; PM records the internal acceptance decision. |

Review and decision time is included in the listed packages; the schedule has no zero-hour tasks for M1–M5.

Each defect has an ID, environment, reproduction steps, expected and actual result, severity, fixer, retest date, and status. A blocker, wrong metric source, or misleading medical claim is resolved before M5 or handled by a documented exception. A file's presence in the repository does not prove it passed independent testing.

## 5. Version control rules

Keep the plan baseline, actual test results, and revised forecasts separate. A changed criterion requires a reason, impact on WBS, schedule, cost, and risks, and a recorded decision. Check each metric against the source for the corresponding data and model version; do not change a value in the report without updating its source map, demo, and QA record.
