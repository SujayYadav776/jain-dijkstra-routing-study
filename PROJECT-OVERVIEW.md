# Dijkstra’s Shortest Path Project — Bengaluru Hospital Routing

## Aim

This project demonstrates how Dijkstra’s algorithm finds the shortest or fastest route from **JAIN University, Jayanagar (A)** to nearby locations, including four hospitals. It uses an ambulance-routing theme to connect classroom calculations with a real-world problem.

## Network and data

The teaching graph contains **13 locations (A–M), 25 corridors and 50 directed connections**. Each direction has its own distance and estimated travel time. Location references come from OpenStreetMap, while OSRM supplies road-route distances and static car-profile times. Google Maps observations provide dated comparisons. Original data was collected on 17 October 2026; Manipal Hospital was added on 20 October 2026.

## How the algorithm works

1. Set the source cost to zero and every other node’s cost to infinity.
2. Select the unsettled node with the smallest known cost.
3. Check its outgoing connections and update any cheaper routes, recording predecessors.
4. Repeat until the destination is settled.
5. Follow the predecessors backwards to recover the route.

Distance weights produce the shortest route; travel-time weights produce the fastest estimated route within the teaching graph. Manual trace tables show every calculation.

## Shortest-distance hospital results

| Hospital | Route from A | Distance |
|---|---|---:|
| Jayadeva (C) | A → B → C | 1,497.0 m |
| Sagar Hospitals (D) | A → B → C → D | 2,695.0 m |
| NIMHANS reference (L) | A → B → C → L | 4,607.9 m |
| Manipal, Jayanagar (M) | A → M | 779.5 m |

## Project activities and outputs

Students explore the interactive HTML graph, calculate routes on paper, test a corridor closure or increased travel time, and compare their routes with the algorithm. Human-recorded journey times from JAIN University to all 12 destinations are now stored in `data/human_journey_times.csv`. Route-choice and calculation-time measurements remain pending. The supplied journey routes, transport modes and observation dates were not provided.

The project includes the website, Python algorithm, source data, trace tables, report, presentation and workbook. The algorithm passed **338 independent correctness comparisons**.

## Interpretation

The results are optimal for this selected teaching graph. Travel times are static estimates, and traffic scenarios are simulations. The project does not establish live ambulance response times or verify hospital entrance access. The HTML displays distance costs divided by 100 and truncated to two decimals, while travel times appear in minutes; calculations retain the original precision.
