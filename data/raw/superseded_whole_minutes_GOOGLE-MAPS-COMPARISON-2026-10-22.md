# Fresh Google Maps comparison — 22 October 2026

22 October 2026, approximately 19:27-19:29 IST. Driving, Leave now; first recommended route recorded.

| Node | Destination | Human (min) | Google (min) | Difference (min) |
|---|---|---:|---:|---:|
| B | Ragigudda bus stop | 8 | 2 | +6 |
| C | Jayadeva Hospital | 10 | 6 | +4 |
| D | Sagar Hospitals | 12 | 9 | +3 |
| E | Jayanagar TTMC | 14 | 9 | +5 |
| F | Jayanagar Metro | 19 | 14 | +5 |
| G | RV Road | 13 | 9 | +4 |
| H | Banashankari bus stop | 26 | 21 | +5 |
| I | Ranga Shankara | 13 | 8 | +5 |
| J | Gopalan Innovation Mall | 14 | 8 | +6 |
| K | Ragigudda Temple | 10 | 4 | +6 |
| L | NIMHANS | 17 | 13 | +4 |
| M | Manipal Hospital Jayanagar | 9 | 4 | +5 |

Difference = human duration minus current Google estimate. B is provisional and excluded from the following summary.

For the other 11 destinations: mean recorded time 14.27 min; mean Google estimate 9.55 min; mean gap 4.73 min. All 11 recorded journeys are longer than the fresh estimates. These averages describe destinations, not repeated trials.

## Interpretation

The current Google snapshots are closer to the recorded journeys than the old snapshots: excluding B, the mean difference is now 4.73 min rather than 7.64 min. Banashankari changed from 8 to 21 min, while its observed time is 26 min. Google explicitly reported much heavier traffic than usual on that route. The fresh search used named places rather than the old snapped road coordinates, so changes also involve endpoint or route differences.

The four hospital observations total 48 min versus 32 min for the fresh recommended estimates. Their mean difference is 4 min. These are separate trips, not one combined route.

NIMHANS recommended time is 13 min with a restricted/private-road warning; a 14-min alternative was also shown. An accessible entrance and route need verification before treating that value as comparable.

This exercise shows why routing weights, observation conditions and endpoint selection matter. It does not prove that either algorithm is inaccurate, nor establish travel-time savings from Dijkstra. Actual recorded routes cannot be reconstructed from total durations alone.

## Method and endpoint notes

Human trip dates, modes, routes and entrance points unknown; these are descriptive comparisons, not contemporaneous prediction errors. Named place searches replace earlier snapped-coordinate endpoints. Changes from old estimates cannot be attributed to traffic alone. B excluded from aggregate statistics because its exact stop reference is unresolved. L includes a restricted-road warning. Route links reproduce named queries but may resolve differently later. Original 17/20 October snapshots retained.

- B: Transit result selected; exact human stop side and original project reference do not match; provisional. [Google Maps route](https://www.google.com/maps/dir/?api=1&origin=JAIN+University+44%2F4+District+Fund+Road+Jayanagar+Bengaluru&destination=Ragigudda+Temple+transit+stop%2C+Putlanpalya&travelmode=driving)
- C: Named destination matched; actual entrance unknown. [Google Maps route](https://www.google.com/maps/dir/?api=1&origin=JAIN+University+44%2F4+District+Fund+Road+Jayanagar+Bengaluru&destination=Jayadeva+Hospital+Bannerghatta+Road+Bengaluru&travelmode=driving)
- D: Named branch matched; actual entrance unknown. [Google Maps route](https://www.google.com/maps/dir/?api=1&origin=JAIN+University+44%2F4+District+Fund+Road+Jayanagar+Bengaluru&destination=Sagar+Hospitals+Jayanagar+Tilak+Nagar+Bengaluru&travelmode=driving)
- E: Named destination matched. [Google Maps route](https://www.google.com/maps/dir/?api=1&origin=JAIN+University+44%2F4+District+Fund+Road+Jayanagar+Bengaluru&destination=Jayanagar+TTMC-BMTC+Bengaluru&travelmode=driving)
- F: Resolved to station named Jayanagar; exact exit or bus stop unverified. [Google Maps route](https://www.google.com/maps/dir/?api=1&origin=JAIN+University+44%2F4+District+Fund+Road+Jayanagar+Bengaluru&destination=Jayanagar+Metro+Station+Bengaluru&travelmode=driving)
- G: Named station matched; 8 min alternative also shown; first recommended route retained. [Google Maps route](https://www.google.com/maps/dir/?api=1&origin=JAIN+University+44%2F4+District+Fund+Road+Jayanagar+Bengaluru&destination=Rashtreeya+Vidyalaya+Road+Metro+Station+Bengaluru&travelmode=driving)
- H: Google reported much heavier traffic than usual. [Google Maps route](https://www.google.com/maps/dir/?api=1&origin=JAIN+University+44%2F4+District+Fund+Road+Jayanagar+Bengaluru&destination=Banashankari+Bus+Stand+Bengaluru&travelmode=driving)
- I: 7 min alternative also shown; first recommended route retained. [Google Maps route](https://www.google.com/maps/dir/?api=1&origin=JAIN+University+44%2F4+District+Fund+Road+Jayanagar+Bengaluru&destination=Ranga+Shankara+JP+Nagar+Bengaluru&travelmode=driving)
- J: User innovation center mapped to project Mall; lighter traffic than usual. [Google Maps route](https://www.google.com/maps/dir/?api=1&origin=JAIN+University+44%2F4+District+Fund+Road+Jayanagar+Bengaluru&destination=Gopalan+Innovation+Mall+Bannerghatta+Road+Bengaluru&travelmode=driving)
- K: Named temple matched; distinct from B transit stop. [Google Maps route](https://www.google.com/maps/dir/?api=1&origin=JAIN+University+44%2F4+District+Fund+Road+Jayanagar+Bengaluru&destination=Ragigudda+Sri+Prasanna+Anjaneya+Swamy+Temple+Bengaluru&travelmode=driving)
- L: Recommended route warns restricted usage or private roads; alternatives 14 min via 28th Main and 16 min via Bannerghatta. [Google Maps route](https://www.google.com/maps/dir/?api=1&origin=JAIN+University+44%2F4+District+Fund+Road+Jayanagar+Bengaluru&destination=NIMHANS+Bengaluru+Hosur+Road&travelmode=driving)
- M: Named branch matched; lighter traffic than usual. [Google Maps route](https://www.google.com/maps/dir/?api=1&origin=JAIN+University+44%2F4+District+Fund+Road+Jayanagar+Bengaluru&destination=Manipal+Hospitals+Jayanagar+45th+Cross+Road+Bengaluru&travelmode=driving)
