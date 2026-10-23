# Google Maps commute-period forecasts

**Departure date:** Friday, 23 October 2026. **Times:** 8:30 am and 6:30 pm IST. **Fetched:** 22 October 2026, approximately 7:35–7:39 pm IST.

Representative commute periods, not a measured maximum or proven busiest hours. Typical ranges transcribed as displayed, not confidence intervals or exact predicted times. Single-valued displays have equal min and max. First recommended route can differ from faster alternatives and between periods. Human trips were not time-matched. Ragigudda bus stop reference is provisional. Existing website and earlier datasets unchanged.

| Node | Destination | Human recording (min) | Google 8:30 am (min) | Google 6:30 pm (min) |
|---|---|---:|---:|---:|
| B | Ragigudda bus stop | 8 | 3 | 3 |
| C | Jayadeva Hospital | 10 | 3–10 | 4–10 |
| D | Sagar Hospitals | 12 | 6–14 | 7–14 |
| E | Jayanagar TTMC | 14 | 7–12 | 7–14 |
| F | Jayanagar Metro | 19 | 8–20 | 10–20 |
| G | RV Road | 13 | 6–16 | 7–14 |
| H | Banashankari bus stop | 26 | 9–22 | 12–30 |
| I | Ranga Shankara | 13 | 5–12 | 6–12 |
| J | Gopalan Innovation Mall | 14 | 7–14 | 7–14 |
| K | Ragigudda Temple | 10 | 4 | 4 |
| L | NIMHANS | 17 | 9–18 | 10–20 |
| M | Manipal Hospital Jayanagar | 9 | 3–6 | 3–8 |

## Findings

- Banashankari shows the largest evening upper value: 12–30 minutes, versus 9–22 in the morning. Its recorded 26-minute journey falls inside the evening range.
- Sagar: recorded 12 minutes; morning 6–14 and evening 7–14. Jayadeva: recorded 10 minutes; morning 3–10 and evening 4–10.
- NIMHANS: recorded 17 minutes; morning 9–18 and evening 10–20, subject to entrance/access verification.
- Manipal: recorded 9 minutes, above the displayed 3–6 morning and 3–8 evening ranges. This is not evidence of a prediction error because the recorded trip date, mode and route are unknown.
- Some recommended routes change between periods. RV Road has a higher morning upper estimate than evening, so evening is not universally busier.

## Experimental conclusion

The forecasts demonstrate that travel-time weights depend on departure time and route selection. Dijkstra optimises the supplied weights; traffic-aware applications supply changing or predicted weights. Record the Google forecast immediately before repeated actual trips on the same route and mode to evaluate prediction accuracy. Do not use these future forecasts to relabel the past recorded trips as rush-hour journeys.

## Endpoint checks

- B: transit autocomplete stop selected, not the temple attraction; exact human stop side still unknown.
- F/G: station destinations used; exact exits or nearby bus-stop endpoints unverified.
- J: user wording innovation center mapped to the project Gopalan Innovation Mall.
- L: NIMHANS Bengaluru near Bangalore Milk Dairy; campus entrance and route access need verification.
- M: duplicate Manipal listing was discarded; retained the same Jayanagar pin as the prior fresh comparison.

Source: Google Maps driving directions browser UI. Detailed distances, routes, capture timestamps and endpoint notes are in data/google_peak_forecasts_2026-10-23.csv.
