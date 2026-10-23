# JAIN University Dijkstra routing study

Open **index.html** in a browser. No server, sign-in or internet connection is required for the explorer. External source links need internet.

## Deliverables
- output/pdf/JAIN-Routing-Report-Updated.pdf - full report, phase-by-phase session guide and printable student worksheet.
- output/JAIN-Routing-Presentation-Manipal.pptx - editable presentation with speaker notes.
- output/JAIN-Routing-Data-Updated.xlsx - results, editable human-measurement area and source data.
- output/teaching-graph.svg - vector diagram.
- data/ - all location, corridor, matrix, result, scenario and manual trace tables.
- dijkstra.py - the algorithm, path scoring and independent correctness check.
- build_study.py - reproduce all numerical outputs from the frozen data.

## Scope
Source A is JAIN University, School of Commerce, 44/4 District Fund Road, Jayanagar 9th Block, Bengaluru. Thirteen total locations include the source. The 25 selected corridors create 50 directed arcs. Reverse weights are independently sourced.

These are selected landmark-to-landmark OSRM road-route corridors, not a complete junction-level street network. A corridor can contain omitted intersections or physically overlap another corridor. Therefore an optimum is an optimum of this teaching graph. In particular, edge distances follow the car-profile routes returned by OSRM, not guaranteed minimum-distance street routes. The public endpoint uses profile weights; the captured route response states weight_name=routability.

Times are static car-profile estimates. They are not observed drives, live traffic, emergency-vehicle ETAs or complete ambulance response times. Building entrance access and last-mile travel are not verified. Node L snaps approximately 200 m from its mapped hospital reference. Google Maps B resolves to a flyover-level destination and is excluded from normal comparison. Other Google observations are approximate endpoint-matched comparisons, not validation of clinical access.

Google Maps values were read from the browser's recommended driving route with Leave now on 17 October 2026, approximately 22:28-22:30 IST (UTC timestamps in the table). Recommended is not necessarily the smallest displayed ETA; some alternatives differed. Origin/destination URLs use OSRM-snapped road coordinates. Google display distances and minutes are rounded. They are snapshots, not a live connection. Manipal (M) was added on 20 October 2026 with a new Google observation at 21:35 IST; its official branch address is https://www.manipalhospitals.com/jayanagar/contact-us/.

## Human data later
Actual journey observations supplied by the user are stored separately in `data/human_journey_times.csv`: 12 destination times from A, in minutes and seconds. See `data/human_journey_times_notes.md` for provenance and missing context. These whole-trip durations are separate from the route-decision/calculation measurements below. The hosted explorer now displays these observations in place of its main modeled journey-time metric, with all 12 values in a separate table. Algorithm time weights remain modeled. The report, presentation and workbook remain earlier snapshots.

Use C, D and L for the principal hospital tasks, and M as an additional hospital task and J as an optional shortest-versus-fastest task. The CSV has fields participant_id, task_id, objective, route, decision_time_s, manual_time_s, familiarity, notes. objective must be distance_m or duration_s. Enter a path like A-B-C. Times can remain blank. Append one row per participant/task/objective. Do not replace blanks with zero.

You can also enter baseline observations in the explorer and export a matching CSV. Put the downloaded file at data/human_input.csv, keeping a backup if existing observations are present. Then run `python build_study.py`. The script validates paths and nonnegative finite times, writes data/human_scored.csv, and preserves the input file. Publication files are snapshots and must be regenerated after analysis updates; they do not automatically read an edited CSV.

## Reproducibility
Python 3.10+ is sufficient for numerical outputs. Run `python build_study.py` from this directory. NetworkX is optional; when installed it adds a library cross-check. In this delivery NetworkX was unavailable, so the code was checked against independent Floyd-Warshall for 338 origin/destination/objective cases plus boundary cases.

Code timings use 21 batches of 100 calls. Median and p95 columns describe the distribution of per-batch means, not individual-call tail latency. The prebuilt graph, file access, source retrieval and trace recording are excluded. See data/verification.json for environment and method.

The report/HTML builder requires ReportLab and the documented Arial fonts. The presentation/workbook builder uses the Codex artifact-tool runtime. End users need none of those tools to view the delivered files.

## Scenarios
BC unavailable removes the two teaching arcs only. BC duration tripled changes static duration weights only. Neither is a measured traffic incident or a physically comprehensive road closure. Production road closures would require rerouting every affected underlying road corridor and preserving turn restrictions across route joins.

## Sources and evidence
JAIN official address: https://www.jainuniversity.ac.in/contact/top-indian-university-with-best-colleges-with-location-maps
OpenStreetMap attribution and licence: https://www.openstreetmap.org/copyright
OSRM HTTP API: https://project-osrm.org/docs/v26.6.1/http
Karnataka historical context (secondary report, 9 December 2020): https://timesofindia.indiatimes.com/city/bengaluru/karnataka-108-ambulance-service-failed-to-provide-service-within-golden-hour-in-50-trauma-cases-says-cag/articleshow/79648476.cms
NHS historical metric specification (25 July 2022): https://www.england.nhs.uk/statistics/wp-content/uploads/sites/2/2022/07/20220725-AmbSYS-specification.pdf

Exact OpenStreetMap feature IDs and geocode URLs are in data/locations.csv. The complete OSRM request is retained in data/study.json and raw/geocodes_and_matrix.json. Machine-readable sources are frozen for reproducibility; source map/extract dates and the public routing server's profile build were not reported by the service. Do not infer them from the access date.

No human observations, GPS photos, measured drives, hospital-entrance validations or clinical outcome evidence are fabricated. Historical emergency-service figures are context, not present-day operational performance or proof of algorithm benefit.

## Updated delivery checks
The Manipal extension passed 338 independent algorithm comparisons and 54 explorer route comparisons. All 13 finalized presentation slides matched their authored renders. The updated report has 11 pages and the workbook has five sheets. Human observation fields remain blank. Native Office app testing was not performed.
