# Human-recorded journey times

The user supplied 12 origin-to-destination times on 22 October 2026 and confirmed that they are actual journey times from JAIN University (A). The observation dates themselves were not supplied. The latest user correction replaces the earlier whole-minute values with minutes and seconds. Exact integer seconds are authoritative; decimal minutes are seconds divided by 60, rounded to six decimals in the CSV. The superseded values are retained in data/raw/superseded_whole_minutes_human_journey_times.csv.

The reported names are mapped to existing project nodes. "Gopalan innovation center" is mapped to J, the project's Gopalan Innovation Mall reference. "Jayanagar metro" maps to F and "RV Road" to G. Exact entrances and endpoint coordinates for these journeys were not supplied.

Routes, departure times, transport modes, participant details and repeated-trial information were not supplied. These fields must not be inferred from the algorithm's routes. The supplied values are recorded observations, not stated averages.

These are complete-trip durations. They do not populate decision_time_s or manual_time_s in human_input.csv, which measure route-choice and calculation activities. They do not replace the graph's individual directed-edge weights. A source-to-destination time alone cannot determine the times of its component edges.

The CSV is stored as a separate observation dataset. On 22 October 2026, the hosted explorer was updated to show these times in its main journey-time display, time comparison and a table of all 12 observations. The report, slides and workbook have not been regenerated with these observations. A comparison with model or Google estimates needs the route, travel mode, departure conditions and endpoint differences to be considered; differences alone do not establish algorithm benefits or traffic effects.
