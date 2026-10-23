"""Reproduce numerical outputs offline from frozen public data. Run: python build_study.py"""
from pathlib import Path
import csv
import datetime
import json
import math
import platform
import statistics
import time
from dijkstra import adjacency, dijkstra, route_cost, self_check

ROOT = Path(__file__).resolve().parent


def write_csv(name, rows, fields=None):
    if fields is None:
        fields = list(rows[0])
    with (ROOT / "data" / name).open("w",newline="",encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f,fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def unpack(raw):
    return json.loads(raw["markdown"].removeprefix("```json").removesuffix("```").strip())


def portable_json(value):
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {k: portable_json(v) for k,v in value.items()}
    if isinstance(value, list):
        return [portable_json(v) for v in value]
    return value


def main():
    study = json.loads((ROOT/"data/study.json").read_text(encoding="utf-8"))
    nodes = json.loads((ROOT/"data/nodes.json").read_text(encoding="utf-8"))
    maps = json.loads((ROOT/"data/google_maps.json").read_text(encoding="utf-8"))
    matrix = study["matrix"]
    edges = []
    for pair in study["pairs"]:
        for a,b in (pair,pair[::-1]):
            i,j = ord(a)-65,ord(b)-65
            edges.append({"source":a,"target":b,"corridor":pair,
                          "distance_m":matrix["distances"][i][j],
                          "duration_s":matrix["durations"][i][j],
                          "basis":"OSRM car-profile corridor; not observed driving", "source_url":study.get("extension_table_url",study["table_url"]) if "M" in pair else study["table_url"]})
    assertions = self_check(edges)
    nx_verified = False
    try:
        import networkx as nx
        for weight in ("distance_m","duration_s"):
            g=nx.DiGraph()
            for e in edges:
                g.add_edge(e["source"],e["target"],weight=e[weight])
            for node in nodes:
                assert math.isclose(nx.dijkstra_path_length(g,"A",node["id"]),dijkstra(adjacency(edges,weight),"A",node["id"])["cost"],abs_tol=1e-7)
        nx_verified = True
    except ImportError:
        pass
    write_csv("edges.csv",edges)
    locations=[]
    for i,n in enumerate(nodes):
        snap=matrix["sources"][i]
        n.update({"road_lon":snap["location"][0],"road_lat":snap["location"][1],"snap_m":snap["distance"],"road_name":snap["name"]})
        n["label"]={"A":"JAIN University (source)","B":"Ragigudda bus stop","C":"Jayadeva hospital","D":"Sagar Hospitals","E":"Jayanagar TTMC","F":"Jayanagar metro bus stop","G":"RV Road station reference","H":"Banashankari bus stop","I":"Ranga Shankara","J":"Gopalan Innovation Mall","K":"Ragigudda Temple","L":"NIMHANS hospital reference","M":"Manipal Hospital, Jayanagar"}[n["id"]]
        locations.append({"id":n["id"],"name":n["label"],"osm_type":n["osm_type"],"osm_id":n["osm_id"],"mapped_lat":float(n["lat"]),"mapped_lon":float(n["lon"]),"road_lat":n["road_lat"],"road_lon":n["road_lon"],"snap_m":round(n["snap_m"],1),"mapped_feature":n["type"],"osm_url":f'https://www.openstreetmap.org/{n["osm_type"]}/{n["osm_id"]}',"geocode_url":n["source_url"]})
    write_csv("locations.csv",locations)
    write_csv("google_maps.csv",[{k:v for k,v in g.items() if k not in ("origin","destination")} for g in maps])
    for key in ("distances","durations"):
        write_csv("osrm_"+key+"_matrix.csv",[{"source":n["id"],**{b["id"]:matrix[key][i][j] for j,b in enumerate(nodes)}} for i,n in enumerate(nodes)])
    results=[]
    traces={}
    for n in nodes[1:]:
        row={"destination":n["id"],"name":n["label"]}
        for weight,prefix in (("distance_m","distance"),("duration_s","time")):
            graph=adjacency(edges,weight)
            result=dijkstra(graph,"A",n["id"],trace=True)
            batches=[]
            for _ in range(21):
                start=time.perf_counter_ns()
                for _ in range(100):
                    dijkstra(graph,"A",n["id"])
                batches.append((time.perf_counter_ns()-start)/100/1e6)
            row.update({prefix+"_route":"-".join(result["route"]),prefix+"_route_m":round(route_cost(edges,result["route"],"distance_m"),1),prefix+"_route_s":round(route_cost(edges,result["route"],"duration_s"),1),prefix+"_settled":result["settled_nodes"],prefix+"_edges_examined":result["examined_edges"],prefix+"_code_median_ms":statistics.median(batches),prefix+"_code_p95_ms":sorted(batches)[19]})
            if n["id"] in "CDJLM":
                traces[n["id"]+"_"+prefix]=result["trace"]
                write_csv("trace_"+n["id"]+"_"+prefix+".csv",[{"step":t["step"],"settled":t["settled"],"settled_cost":t["cost"],"updated":",".join(t["updated"]),**{a:(round(v,1) if math.isfinite(v) else "INF") for a,v in sorted(t["distances"].items())},"predecessors":"; ".join(a+":"+b for a,b in sorted(t["previous"].items()))} for t in result["trace"]])
        i=ord(n["id"])-65
        gm=next(g for g in maps if g["id"]==n["id"])
        row.update({"osrm_reference_m":matrix["distances"][0][i],"osrm_reference_s":matrix["durations"][0][i],"google_recommended_m":gm["distance_m"],"google_recommended_min":gm["eta_min"],"google_comparable":gm["comparable"],"graph_distance_difference_vs_osrm_percent":round(100*(row["distance_route_m"]/matrix["distances"][0][i]-1),2),"graph_time_difference_vs_osrm_percent":round(100*(row["time_route_s"]/matrix["durations"][0][i]-1),2)})
        results.append(row)
    write_csv("results.csv",results)
    scenarios=[]
    for target in "CDJLM":
        for weight in ("distance_m","duration_s"):
            for label,blocked,multipliers in [("baseline",[],{}),("BC corridor unavailable",["BC"],{}),("BC duration tripled",[],{"BC":3})]:
                changed=[dict(e) for e in edges]
                for e in changed:
                    e["duration_s"]*=multipliers.get(e["corridor"],1)
                path=dijkstra(adjacency(changed,weight,blocked),"A",target)["route"]
                scenarios.append({"destination":target,"objective":weight,"scenario":label,"route":"-".join(path),"distance_m":round(route_cost(changed,path,"distance_m"),1),"modeled_duration_s":round(route_cost(changed,path,"duration_s"),1),"basis":"Controlled teaching scenario, not an observed road closure or traffic event"})
    write_csv("scenarios.csv",scenarios)
    human_fields=["participant_id","task_id","objective","route","decision_time_s","manual_time_s","familiarity","notes"]
    human_path=ROOT/"data/human_input.csv"
    if not human_path.exists():
        write_csv("human_input.csv",[{"participant_id":"", "task_id":task,"objective":obj,"route":"","decision_time_s":"","manual_time_s":"","familiarity":"","notes":""} for task in "CDJLM" for obj in ("distance_m","duration_s")],human_fields)
    scored=[]
    with human_path.open(encoding="utf-8-sig",newline="") as f:
        for r in csv.DictReader(f):
            if not r["route"].strip():
                continue
            if r["task_id"] not in "CDJLM" or len(r["task_id"])!=1 or r["objective"] not in ("distance_m","duration_s"):
                raise ValueError("Human row contains invalid task or objective")
            path=r["route"].upper().replace(" ","").split("-")
            if path[0]!="A" or path[-1]!=r["task_id"]:
                raise ValueError("Human route must start at A and end at the task destination")
            for field in ("decision_time_s","manual_time_s"):
                if r[field] and (not math.isfinite(float(r[field])) or float(r[field])<0):
                    raise ValueError("Human times must be finite and nonnegative")
            cost=route_cost(edges,path,r["objective"])
            optimal=dijkstra(adjacency(edges,r["objective"]),"A",r["task_id"])["cost"]
            scored.append({**r,"chosen_cost":round(cost,1),"optimal_cost":round(optimal,1),"route_gap_percent":round(100*(cost/optimal-1),2)})
    write_csv("human_scored.csv",scored,human_fields+["chosen_cost","optimal_cost","route_gap_percent"])
    (ROOT/"data/compiled.json").write_text(json.dumps(portable_json({"nodes":nodes,"edges":edges,"results":results,"scenarios":scenarios,"traces":traces,"google":maps,"study":study,"human":scored}),indent=2,allow_nan=False),encoding="utf-8")
    verification={"all_pairs_floyd_warshall_comparisons":assertions,"boundary_cases":"unreachable, same source/target, zero edge, equal-cost alternatives, negative weight rejection", "networkx_verified":nx_verified,"benchmark":{"python":platform.python_version(),"platform":platform.platform(),"measurement":"21 batches x 100 calls; median and nearest-rank p95 of per-batch mean milliseconds; graph prebuilt; no I/O, tracing, or network"},"nodes":len(nodes),"directed_edges":len(edges),"corridors":len(study["pairs"]),"human_records":len(scored)}
    (ROOT/"data/verification.json").write_text(json.dumps(verification,indent=2),encoding="utf-8")
    print(json.dumps(verification,indent=2))
    for r in results:
        print(r["destination"],r["distance_route"],r["distance_route_m"],r["time_route"],r["time_route_s"])


if __name__ == "__main__":
    main()
