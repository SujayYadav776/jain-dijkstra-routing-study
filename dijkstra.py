"""Dijkstra for the frozen 13-location teaching graph. Python standard library only."""
import heapq
import math


def adjacency(edges, weight="distance_m", blocked=()):
    graph = {}
    for e in edges:
        graph.setdefault(e["source"], [])
        graph.setdefault(e["target"], [])
        if e["corridor"] in blocked:
            continue
        value = e[weight]
        if not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
            raise ValueError("Dijkstra requires finite, nonnegative edge weights")
        graph[e["source"]].append((e["target"], value))
    for neighbors in graph.values():
        neighbors.sort()
    return graph


def dijkstra(graph, source, target=None, trace=False):
    if source not in graph or (target is not None and target not in graph):
        raise ValueError("Unknown source or destination")
    dist = {node: math.inf for node in graph}
    previous = {}
    dist[source] = 0
    heap = [(0, source)]
    settled = set()
    history = []
    examined = 0
    while heap:
        cost, node = heapq.heappop(heap)
        if node in settled or cost != dist[node]:
            continue
        settled.add(node)
        updates = []
        if node != target:
            for neighbor, weight in graph[node]:
                examined += 1
                candidate = cost + weight
                if neighbor not in settled and candidate < dist[neighbor]:
                    dist[neighbor] = candidate
                    previous[neighbor] = node
                    heapq.heappush(heap, (candidate, neighbor))
                    updates.append(neighbor)
        if trace:
            history.append({"step": len(history)+1, "settled": node,
                            "cost": cost, "updated": updates,
                            "distances": dict(dist), "previous": dict(previous)})
        if node == target:
            break
    route = []
    if target is not None and math.isfinite(dist[target]):
        node = target
        while node != source:
            route.append(node)
            node = previous[node]
        route.append(source)
        route.reverse()
    return {"cost": dist.get(target) if target is not None else None,
            "distances": dist, "route": route, "trace": history,
            "settled_nodes": len(settled), "examined_edges": examined}


def route_cost(edges, path, weight):
    lookup = {(e["source"], e["target"]): e[weight] for e in edges}
    if not path:
        raise ValueError("Route is empty")
    try:
        return sum(lookup[a, b] for a, b in zip(path, path[1:]))
    except KeyError as exc:
        raise ValueError("Route contains an unavailable directed corridor: %s" % (exc.args[0],)) from exc


def self_check(edges):
    """Compare every pair with independent Floyd-Warshall, plus boundary cases."""
    comparisons = 0
    for weight in ("distance_m", "duration_s"):
        graph = adjacency(edges, weight)
        nodes = sorted(graph)
        ref = {(a,b): 0.0 if a == b else math.inf for a in nodes for b in nodes}
        for a in nodes:
            for b,w in graph[a]:
                ref[a,b] = min(ref[a,b], w)
        for k in nodes:
            for a in nodes:
                for b in nodes:
                    ref[a,b] = min(ref[a,b], ref[a,k]+ref[k,b])
        for a in nodes:
            for b in nodes:
                result = dijkstra(graph,a,b)
                assert math.isclose(result["cost"], ref[a,b], abs_tol=1e-7)
                assert math.isclose(route_cost(edges,result["route"],weight), ref[a,b], abs_tol=1e-7)
                comparisons += 1
    assert dijkstra({"A":[], "B":[]},"A","B")["route"] == []
    assert dijkstra({"A":[]},"A","A")["route"] == ["A"]
    assert dijkstra({"A":[("B",0)],"B":[]},"A","B")["cost"] == 0
    assert dijkstra({"A":[("B",1),("C",1)],"B":[("D",1)],"C":[("D",1)],"D":[]},"A","D")["cost"] == 2
    try:
        adjacency([{"source":"A","target":"B","corridor":"AB","distance_m":-1}])
        raise AssertionError("Negative weight accepted")
    except ValueError:
        pass
    return comparisons
