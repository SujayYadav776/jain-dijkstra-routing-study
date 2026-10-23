"""Create the report and self-contained explorer from compiled study data."""
from pathlib import Path
import json, math, html, csv, sys, statistics
from decimal import Decimal, ROUND_HALF_UP
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Line, Circle, String, Polygon
from reportlab.graphics import renderSVG

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'output'
(OUT/'pdf').mkdir(parents=True,exist_ok=True)
S=json.loads((ROOT/'data/compiled.json').read_text(encoding='utf-8'))
RESULT={r['destination']:r for r in S['results']}
NODES={n['id']:n for n in S['nodes']}
with (ROOT/'data/human_vs_google_evening_upper.csv').open(encoding='utf-8-sig',newline='') as f:
    HUMAN_GOOGLE={r['destination']:r for r in csv.DictReader(f)}
with (ROOT/'data/osrm_distances_matrix.csv').open(encoding='utf-8-sig',newline='') as f:
    DIST_MATRIX=list(csv.reader(f))
with (ROOT/'data/osrm_durations_matrix.csv').open(encoding='utf-8-sig',newline='') as f:
    TIME_MATRIX=list(csv.reader(f))
POS={'A':(450,330),'B':(580,390),'C':(815,290),'D':(815,145),'E':(290,145),'F':(100,145),'G':(150,320),'H':(75,545),'I':(315,640),'J':(815,565),'K':(580,595),'L':(590,55),'M':(420,440)}
INK=colors.HexColor('#142b33'); GREEN=colors.HexColor('#00685d'); PALE=colors.HexColor('#e5eeea'); ORANGE=colors.HexColor('#a74720')
BLUE=colors.HexColor('#2478a5'); AMBER=colors.HexColor('#b37a16'); RED=colors.HexColor('#c5584a'); TEAL=colors.HexColor('#008475')
pdfmetrics.registerFont(TTFont('Arial','C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('Arial-Bold','C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='Arial-Bold',italic='Arial',boldItalic='Arial-Bold')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='Text',fontName='Arial',fontSize=10,leading=15,textColor=INK,spaceAfter=9))
styles.add(ParagraphStyle(name='SmallText',fontName='Arial',fontSize=8,leading=11,textColor=INK,spaceAfter=5))
styles.add(ParagraphStyle(name='TitleCustom',fontName='Arial-Bold',fontSize=29,leading=35,textColor=INK,spaceAfter=18))
styles.add(ParagraphStyle(name='HeadingCustom',fontName='Arial-Bold',fontSize=19,leading=24,textColor=GREEN,spaceAfter=13))
styles.add(ParagraphStyle(name='SubCustom',fontName='Arial-Bold',fontSize=12,leading=17,textColor=INK,spaceBefore=8,spaceAfter=7))

def minutes(seconds):
    return str((Decimal(str(seconds))/Decimal(60)).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP))

def p(text,style='Text'):
    return Paragraph(text,styles[style])

def table(headers,rows,widths=None,font=8.5):
    style_name=f'TableCell{font}'
    if style_name not in styles.byName:
        styles.add(ParagraphStyle(name=style_name,parent=styles['SmallText'],fontSize=font,leading=font+2,spaceAfter=0))
    cells=[[p(html.escape(str(v)),style_name) for v in row] for row in [headers]+rows]
    t=Table(cells,colWidths=widths,repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),PALE),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),('LINEBELOW',(0,0),(-1,0),1,GREEN),('LINEBELOW',(0,1),(-1,-1),.3,colors.HexColor('#d5ddda'))]))
    return t

def graph(width=490,height=310,path=('A','B','C')):
    d=Drawing(width,height)
    def xy(a):
        x,y=POS[a];return x/920*width,height-y/730*height
    pairs=set(zip(path,path[1:]))
    for corridor in S['study']['pairs']:
        a,b=corridor;x1,y1=xy(a);x2,y2=xy(b)
        chosen=(a,b) in pairs or (b,a) in pairs
        line=Line(x1,y1,x2,y2,strokeColor=GREEN if chosen else colors.HexColor('#bcc9c6'),strokeWidth=2.6 if chosen else .8)
        d.add(line)
        if chosen:
            if (b,a) in pairs:x1,y1,x2,y2=x2,y2,x1,y1
            vx,vy=x2-x1,y2-y1;norm=math.hypot(vx,vy);ux,uy=vx/norm,vy/norm
            tx,ty=x2-ux*17,y2-uy*17
            d.add(Polygon([tx,ty,tx-ux*9-uy*4,ty-uy*9+ux*4,tx-ux*9+uy*4,ty-uy*9-ux*4],fillColor=GREEN,strokeColor=GREEN))
    for node in S['nodes']:
        x,y=xy(node['id']);chosen=node['id'] in path
        d.add(Circle(x,y,12,fillColor=GREEN if chosen else colors.white,strokeColor=GREEN if chosen else INK,strokeWidth=1))
        d.add(String(x,y-3.5,node['id'],fontName='Arial-Bold',fontSize=10,textAnchor='middle',fillColor=colors.white if chosen else INK))
    return d

def comparison_chart(kind):
    rows=[(k,HUMAN_GOOGLE[k]) for k in 'CDEFGHIJKLM']
    width,height=510,430
    d=Drawing(width,height)
    left,right=145,475; plot=right-left; top=28; row_h=30
    def label(x,y,text,size=7,color=INK,anchor='start'):
        d.add(String(x,y,text,fontName='Arial',fontSize=size,fillColor=color,textAnchor=anchor))
    if kind=='paired':
        for minute in range(0,31,5):
            x=left+plot*minute/30
            d.add(Line(x,top-6,x,top+len(rows)*row_h,strokeColor=colors.HexColor('#dce4df'),strokeWidth=.6))
            label(x,top+len(rows)*row_h+8,str(minute),7,INK,'middle')
        label((left+right)/2,8,'Minutes',8,INK,'middle')
        for i,(key,r) in enumerate(rows):
            y=height-top-(i+1)*row_h+8
            label(0,y+2,NODES[key]['label'][:22],7)
            human=int(r['human_journey_s']); google=int(r['google_evening_upper_min'])*60
            for value,offset,color in [(human,5,BLUE),(google,16,AMBER)]:
                w=plot*(value/60)/30
                from reportlab.graphics.shapes import Rect
                d.add(Rect(left,y+offset,w,7,fillColor=color,strokeColor=None))
                label(min(left+w+3,490),y+offset+1,f'{value//60}:{value%60:02d}',6.5)
        label(left, height-13,'Blue: human-recorded   Amber: Google upper prediction',7,INK)
    elif kind=='difference':
        center=(left+right)/2; scale=38
        diffrows=sorted(rows,key=lambda kv:int(kv[1]['difference_s']),reverse=True)
        for m in range(-4,5,2):
            x=center+scale*m
            d.add(Line(x,top-5,x,top+len(rows)*row_h,strokeColor=AMBER if m==0 else colors.HexColor('#dce4df'),strokeWidth=1 if m==0 else .6))
            label(x,top+len(rows)*row_h+8,str(m),7,INK,'middle')
        label((left+right)/2,8,'Human minus Google upper prediction (minutes)',8,INK,'middle')
        for i,(key,r) in enumerate(diffrows):
            y=height-top-(i+1)*row_h+8; value=int(r['difference_s'])/60
            label(0,y+4,NODES[key]['label'][:22],7)
            x=center+scale*value; start=min(center,x); w=max(abs(x-center),.8)
            from reportlab.graphics.shapes import Rect
            d.add(Rect(start,y,w,10,fillColor=RED if value>0 else TEAL,strokeColor=None))
            label(x+(4 if value>=0 else -4),y+2,f'{"+" if value>0 else "−"}{abs(int(r["difference_s"]))//60}:{abs(int(r["difference_s"]))%60:02d}',6.5,INK,'start' if value>=0 else 'end')
        label(left,height-13,'Right / red: longer human trip   Left / teal: shorter human trip',7,INK)
    else:
        size=330; x0=93; y0=54; max_min=30; scale=size/max_min
        for m in range(0,31,5):
            x=x0+m*scale; y=y0+m*scale
            d.add(Line(x,y0,x,y0+size,strokeColor=colors.HexColor('#dce4df'),strokeWidth=.6))
            d.add(Line(x0,y,x0+size,y,strokeColor=colors.HexColor('#dce4df'),strokeWidth=.6))
            label(x,y0-13,str(m),7,INK,'middle');label(x0-10,y-2,str(m),7,INK,'end')
        d.add(Line(x0,y0,x0+size,y0+size,strokeColor=AMBER,strokeWidth=1.5))
        label(x0+size/2,y0-31,'Google upper prediction (minutes)',8,INK,'middle')
        label(8,y0+size/2,'Human time (minutes)',8,INK)
        for key,r in rows:
            x=x0+scale*int(r['google_evening_upper_min']); y=y0+scale*int(r['human_journey_s'])/60
            d.add(Circle(x,y,4,fillColor=RED if int(r['difference_s'])>0 else TEAL,strokeColor=colors.white,strokeWidth=.8))
            label(x+5,y+3,key,7)
        label(x0,height-13,'Above the diagonal: longer human trip. Below: shorter.',7,INK)
    return d

def all_simple_routes(target,weight):
    out={n:[] for n in NODES}
    for e in S['edges']: out[e['source']].append(e)
    found=[]; path=['A']; seen={'A'}
    def visit(node,cost):
        if node==target:
            found.append((cost,path.copy())); return
        for edge in out[node]:
            nxt=edge['target']
            if nxt in seen: continue
            seen.add(nxt);path.append(nxt);visit(nxt,cost+edge[weight]);path.pop();seen.remove(nxt)
    visit('A',0)
    return sorted(found,key=lambda x:(x[0],''.join(x[1])))[:5]

def trace_table(trace,weight):
    def show(value):
        return f'{value:.1f}' if weight=='distance_m' else f'{value:.1f} s ({value/60:.2f} min)'
    rows=[]
    for t in trace:
        updates=', '.join(f"{n}={show(t['distances'][n])} via {t['previous'][n]}" for n in t['updated']) or 'No label improved'
        rows.append([t['step'],t['settled'],show(t['cost']),updates])
    return table(['Step','Settled','Current cost','Improved tentative labels'],rows,[35,55,105,316],7.5)

def matrix_table(matrix,unit):
    header=matrix[0]
    rows=[]
    for row in matrix[1:]:
        rows.append([row[0]]+[f'{float(v):.1f}' for v in row[1:]])
    cells=[[p(str(v),'SmallText') for v in r] for r in [header]+rows]
    t=Table(cells,colWidths=[36]+[36]*(len(header)-1),repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),PALE),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('ALIGN',(1,1),(-1,-1),'RIGHT'),('LEFTPADDING',(0,0),(-1,-1),2),('RIGHTPADDING',(0,0),(-1,-1),2),('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),('LINEBELOW',(0,0),(-1,0),1,GREEN),('LINEBELOW',(0,1),(-1,-1),.3,colors.HexColor('#d5ddda'))]))
    return t

def chart(metric):
    width,height=480,190;d=Drawing(width,height)
    cats=['C','D','J','L'];maxv=max(RESULT[k]['distance_route_m']/1000 if metric=='distance' else RESULT[k]['time_route_s']/60 for k in cats)
    scale=300/maxv
    for i,k in enumerate(cats):
        value=RESULT[k]['distance_route_m']/1000 if metric=='distance' else RESULT[k]['time_route_s']/60
        y=150-i*42
        from reportlab.graphics.shapes import Rect
        d.add(String(0,y+3,k,fontName='Arial-Bold',fontSize=10,fillColor=INK))
        d.add(Rect(30,y,value*scale,18,fillColor=GREEN,strokeColor=None))
        d.add(String(40+value*scale,y+3,f'{value:.2f} '+('km' if metric=='distance' else 'min'),fontName='Arial',fontSize=10,fillColor=INK))
    return d

def page(title):
    return [PageBreak(),p(title,'HeadingCustom')]

story=[p('Every Minute Counts','TitleCustom'),p("A complete experiential learning study of Dijkstra's shortest path algorithm",'HeadingCustom'),p('<b>Starting point:</b> JAIN (Deemed-to-be University), School of Commerce, 44/4 District Fund Road, behind Smart Bazaar, Jayanagara 9th Block, Bengaluru 560041.'),p('This report brings the complete study into one document: locations, road references, all graph costs, the algorithm, hand-worked traces, route alternatives, human journey observations, Google busy-period predictions, comparison charts, controlled scenarios, learning-session plan, interpretation, and source notes.'),p('Study question','SubCustom'),p('How does Dijkstra select the lowest-cost route in a small directed graph, how do distance and modeled driving time change the preferred path, and how do supplied human journey times compare descriptively with Google Maps busy-period predictions?'),p('Main findings','SubCustom')]
story += [table(['Hospital','Shortest-distance route','Graph distance','Fastest-profile route','Graph profile time'],[[k,RESULT[k]['distance_route'],f"{RESULT[k]['distance_route_m']/1000:.3f} km",RESULT[k]['time_route'],f"{minutes(RESULT[k]['time_route_s'])} min"] for k in 'CDLM'],[56,124,73,124,76],7.5)]
valid_diffs=[int(HUMAN_GOOGLE[k]['difference_s']) for k in 'CDEFGHIJKLM']
story += [Spacer(1,10),p(f"The recorded trip was at or below Google's selected upper prediction for {sum(x<=0 for x in valid_diffs)} of 11 comparable destinations. The median human-minus-Google difference was {abs(int(statistics.median(valid_diffs)))//60} min {abs(int(statistics.median(valid_diffs)))%60:02d} sec, with the human trip shorter. Ragigudda bus stop (B) is excluded because its Google endpoint is provisional."),p('What the result means','SubCustom'),p('Dijkstra is optimal for the graph and objective supplied to it. It does not make a larger road network, traffic forecast, or ambulance response system optimal. Here, edge costs are static car-profile estimates, while the human values are complete trips whose route, mode, and departure conditions were not supplied. The comparison is descriptive; it cannot measure Dijkstra accuracy or an effect on emergency response.'),p('Scope and evidence','SubCustom'),p('The graph contains 13 locations and 25 selected corridor pairs, represented by 50 independently weighted directed arcs. Human journey durations are supplied for all 12 destinations. There are no human route-choice, decision-time, or manual-calculation observations in the project data. No measured-route, GPS, hospital-entrance, or clinical-outcome claim is made.')]

story += page('Phase 1 - Locations and road references')
story += [p('A is the source for all trips. The hospital references are C, D, L and M. Stops, stations, a theatre, a mall and a temple provide additional graph structure. The graph points are mapped features snapped to a car-accessible road network; the listed offset is not added to route costs.'),table(['ID','Selected location','Mapped latitude, longitude','Road snap'],[[n['id'],n['label'],f"{float(n['lat']):.6f}, {float(n['lon']):.6f}",f"{n['snap_m']:.1f} m"] for n in S['nodes']],[30,220,170,75],7.5),p('Manipal Hospitals, Jayanagar is the named branch. Its official address is 45/1, 45th Cross, Jayanagara 9th Block. The graph uses its mapped hospital reference snapped about 21 m to a road. The exact entrance is not verified. [S6]','SmallText'),p('Endpoint and feature notes','SubCustom'),p('F is a bus stop named Jayanagara Metro Station, rather than a rail-platform coordinate. G is a station reference snapped to a road. H is the Banashankari bus stop. B refers to the Ragigudda bus stop, distinct from temple K. J is the mapped Gopalan Innovation Mall reference; the supplied “innovation center” trip is matched to it. L is a NIMHANS campus reference with the largest road snap, about 200 m. Hospital, temple, station and bus-stop entrances were not verified. [S1, S2]')]

story += page('Phase 1 - The 13-location teaching graph')
story += [graph(),p('Highlighted path: A-B-C. Lines are selected road-route corridors, not street shapes. Each pair has a separate cost in each direction. Crossing lines do not create graph junctions. [S2]','SmallText'),table(['ID','Location','ID','Location'],[[a,NODES[a]['label'],b,NODES[b]['label'] if b else ''] for a,b in zip('ABCDEFG',['H','I','J','K','L','M',''])],[30,215,30,220],7.5),p('Model boundaries','SubCustom'),p('Each of the 25 displayed corridors uses a selected cell from the road-routing matrix. Intermediate roads and junctions remain hidden inside a corridor. Separately routed corridors may overlap or reverse direction physically; joining them can omit turn-history rules or create redundant travel. Therefore, “optimal” means optimal over this teaching graph, not over every legal Bengaluru street route. A production route model would use road-level segments, turn restrictions, vehicle access, live closures, and verified destination entrances.')]

story += page('Phase 1 - Complete directed corridor costs')
rows=[]
for pair in S['study']['pairs']:
    f=next(e for e in S['edges'] if e['source']==pair[0] and e['target']==pair[1]);r=next(e for e in S['edges'] if e['source']==pair[1] and e['target']==pair[0])
    rows.append([pair,f"{f['distance_m']:.1f}",f"{r['distance_m']:.1f}",f"{f['duration_s']:.1f}",f"{r['duration_s']:.1f}"])
story += [p('Forward is first node to second node; reverse is second node to first. Distances are metres and durations are seconds from a static car-routing profile. The route API selects a profile route; these are not surveyed distances or observed segment times.'),table(['Corridor','Forward m','Reverse m','Forward s','Reverse s'],rows,[75,105,105,105,105],7.5),p('The 25 corridor pairs form 50 directed arcs. Reverse costs are independently read from the road matrix, not copied from forward costs. The full 13-by-13 source-to-destination matrices follow in the appendices. [S2, S3]','SmallText')]

story += page('Appendix A - Full road-routing distance matrix')
story += [p('All mapped nodes are included. Each cell is the road-route distance in metres from the row node to the column node. These matrix values are broader source data; only the 25 selected corridor pairs above are edges in the teaching graph.'),matrix_table(DIST_MATRIX,'m')]
story += page('Appendix B - Full road-routing duration matrix')
story += [p('All mapped nodes are included. Each cell is the static car-profile duration in seconds from the row node to the column node. Values are not human travel times or live traffic forecasts.'),matrix_table(TIME_MATRIX,'s')]

story += page('Phase 2 - Dijkstra method and correctness')
story += [p('For one selected destination and one non-negative edge weight, Dijkstra maintains a tentative cost for every node and a predecessor for each improved label.'),p('<b>Hand calculation:</b> (1) Set A=0 and every other node to infinity. (2) Choose the unsettled node with the smallest tentative cost. (3) For each outgoing directed edge, add its weight to the settled cost. (4) Replace a neighbour’s tentative cost and predecessor only when this new total is smaller. (5) Repeat until the destination is settled. Follow predecessor links backward to reconstruct the route.'),p('Worked example - A to C by distance','SubCustom'),table(['Step','Settled','Cost (m)','Improved tentative labels'],[[t['step'],t['settled'],f"{t['cost']:.1f}",', '.join(f"{k}={t['distances'][k]:.1f} via {t['previous'][k]}" for k in t['updated']) or 'No improvement'] for t in S['traces']['C_distance']],[40,50,75,330],7.2),p('The predecessor chain is C ← B ← A, so the route is A-B-C. Its distance is 618.5 + 878.5 = 1,497.0 m. Its static duration on the same route is 58.7 + 72.2 = 130.9 s (2.18 min). The algorithm’s distance display in the dashboard divides metres by 100 and truncates to two decimals; the report uses metres and kilometres.'),p('Implementation and verification','SubCustom'),p('The implementation uses a min-heap, tentative labels, predecessor pointers, stale-entry checks, and a settled set. Node-ID tie-breaking makes equal costs deterministic. Its usual binary-heap complexity is O((V+E) log V). Independent Floyd-Warshall calculations checked 169 source-destination pairs for distance and 169 for duration (338 cost comparisons); paths were reconstructed and checked. Boundary cases covered unreachable destinations, source equal to target, a zero-weight edge, equal-cost alternatives, and rejection of negative weights.'),p('Code timing method','SubCustom'),p('The graph is prebuilt. Each destination/objective uses 21 batches of 100 calls; the reported median and nearest-rank 95th percentile summarize the batch means in milliseconds. File access, network calls, manual tracing, and human work are excluded. These tiny local measurements illustrate computation, not city-scale performance.')]

story += page('Phase 2 - Route outcomes across all destinations')
story += [p('The teaching graph is compared with the direct OSRM road-profile reference for the same mapped points. The graph distance-optimal and time-optimal routes may differ. Direct OSRM is not a ground-truth check of Dijkstra; it uses a larger road graph and the same general profile-based assumptions.'),table(['ID','Distance-optimal route','Graph km','Fastest route','Graph min','Direct road km','Direct road min'],[[r['destination'],r['distance_route'],f"{r['distance_route_m']/1000:.3f}",r['time_route'],f"{minutes(r['time_route_s'])}",f"{r['osrm_reference_m']/1000:.3f}",f"{r['osrm_reference_s']/60:.2f}"] for r in S['results']],[26,102,51,91,48,73,74],6.5),p('A short route may leave the teaching graph because its corridor set is sparse. For example, L’s graph route is longer than its direct road reference because the graph exposes only selected connections. That is a modeling limitation, not a shortest-path algorithm error.'),p('Shortest distance versus fastest modeled time','SubCustom'),table(['Objective','Route to J','Distance','Modeled duration'],[['Distance',RESULT['J']['distance_route'],f"{RESULT['J']['distance_route_m']:.1f} m",f"{RESULT['J']['distance_route_s']:.1f} s"],['Time',RESULT['J']['time_route'],f"{RESULT['J']['time_route_m']:.1f} m",f"{RESULT['J']['time_route_s']:.1f} s"]],[75,130,130,145],7.5),p('A-K-J is shorter by distance. A-B-J is longer, but its profile duration is lower. “Shortest” and “fastest” are different optimization objectives and must not be treated as interchangeable.')]

story += page('Phase 2 - Local computation measurements')
story += [p('Median and p95 below are milliseconds per call, estimated from the mean of each batch. The machine and graph were local; these values are not a service-level performance measure.'),table(['ID','Distance route','Median ms','p95 ms','Time route','Median ms','p95 ms'],[[r['destination'],r['distance_route']+f" ({r['distance_route_m']/1000:.2f} km)",f"{r['distance_code_median_ms']:.4f}",f"{r['distance_code_p95_ms']:.4f}",r['time_route']+f" ({minutes(r['time_route_s'])} min)",f"{r['time_code_median_ms']:.4f}",f"{r['time_code_p95_ms']:.4f}"] for r in S['results']],[25,100,55,55,95,55,55],6.5),p('The graph is small enough that calculation time is negligible beside route choice, data quality, travel, and endpoint validation. These timings do not compare Dijkstra with a live navigation service.')]

story += page('Phase 2 - Alternative routes to the hospitals')
alt_rows=[]
for target in 'CDLM':
    for objective,weight in [('Distance','distance_m'),('Modeled time','duration_s')]:
        for rank,(cost,path_nodes) in enumerate(all_simple_routes(target,weight),1):
            length=sum(next(e['distance_m'] for e in S['edges'] if e['source']==a and e['target']==b) for a,b in zip(path_nodes,path_nodes[1:]))
            duration=sum(next(e['duration_s'] for e in S['edges'] if e['source']==a and e['target']==b) for a,b in zip(path_nodes,path_nodes[1:]))
            alt_rows.append([target,objective,rank,'-'.join(path_nodes),f'{length/1000:.3f} km',f'{duration/60:.2f} min'])
story += [p('The dashboard lists up to five simple paths per selected destination, ranked by the chosen objective. The list below records the five lowest-cost routes by distance and by modeled time for each hospital. Distances shown are teaching-graph sums; human journey times are separate complete trips.'),table(['Hospital','Ranked by','Route','Path','Distance','Profile time'],[[r[0],r[1],r[2],r[3],r[4],r[5]] for r in alt_rows],[47,80,40,120,70,75],7)]

story += page('Phase 2 - Controlled corridor scenarios')
scenario_rows=[[r['destination'],r['objective'].replace('_m','').replace('_s',''),r['scenario'],r['route'],f"{r['distance_m']/1000:.3f} km",f"{r['modeled_duration_s']/60:.2f} min"] for r in S['scenarios']]
story += [p('The teaching scenario either removes corridor BC in both directions or triples only its static duration. Distances are unaffected by the duration change. These are controlled changes to the teaching graph; they do not simulate a measured congestion event or recompute all overlapping streets.'),table(['Target','Optimize','Scenario','Selected route','Distance','Profile time'],scenario_rows,[42,60,145,95,70,80],6.6),p('The scenario lets students predict and test how Dijkstra responds to altered edge weights or connectivity. If a real street closure affects overlapping corridors, every affected road segment and junction must be rerouted before drawing a real-world conclusion.')]

story += page('Phase 2 - Full hand-worked hospital traces')
story += [p('Each trace shows every settled node until the target is settled, for both distance and modeled-time objectives. An “improvement” records the new tentative label and its predecessor. Distance is in metres; profile time is in seconds, with minutes shown in parentheses.'),p('C - Jayadeva hospital','SubCustom'),trace_table(S['traces']['C_distance'],'distance_m'),Spacer(1,8),trace_table(S['traces']['C_time'],'duration_s'),p('Reconstruction: A-B-C for both objectives. Distance 1,497.0 m; modeled duration 130.9 s.','SmallText')]
story += page('Phase 2 - Full hand-worked hospital traces: D')
story += [p('D - Sagar Hospitals','SubCustom'),trace_table(S['traces']['D_distance'],'distance_m'),Spacer(1,8),trace_table(S['traces']['D_time'],'duration_s'),p('Reconstruction: A-B-C-D for both objectives. Distance 2,695.0 m; modeled duration 216.7 s.','SmallText')]
story += page('Phase 2 - Full hand-worked hospital traces: L')
story += [p('L - NIMHANS hospital reference','SubCustom'),trace_table(S['traces']['L_distance'],'distance_m'),Spacer(1,8),trace_table(S['traces']['L_time'],'duration_s'),p('Reconstruction: A-B-C-L for both objectives. Distance 4,607.9 m; modeled duration 368.2 s. The mapped hospital reference snaps about 200 m to a road; entrance access is unverified.','SmallText')]
story += page('Phase 2 - Full hand-worked hospital traces: M')
story += [p('M - Manipal Hospital, Jayanagar','SubCustom'),trace_table(S['traces']['M_distance'],'distance_m'),Spacer(1,8),trace_table(S['traces']['M_time'],'duration_s'),p('Reconstruction: A-M for both objectives. Distance 779.5 m; modeled duration 64.5 s. The graph ends at a nearby road reference, not a verified entrance.','SmallText')]

story += page('Phase 3 - Human journey times and Google predictions')
comparison_rows=[]
for k in 'BCDEFGHIJKLM':
    r=HUMAN_GOOGLE[k]; hs=int(r['human_journey_s']); gs=int(r['google_evening_upper_min'])*60; diff=int(r['difference_s'])
    comparison_rows.append([k,NODES[k]['label'],f'{hs//60} min {hs%60:02d} sec',f"{gs//60} min",f"{'+' if diff>0 else '−' if diff<0 else ''}{abs(diff)//60} min {abs(diff)%60:02d} sec",'Provisional endpoint' if r['include_in_summary'].lower()=='false' else ('Human longer' if diff>0 else 'Human shorter' if diff<0 else 'Equal')])
story += [p('The human values are actual journey durations supplied for trips from JAIN University. Google’s prediction is the upper end of the saved busy-period driving estimate. The Google value is a forecast snapshot, not live traffic and not a guaranteed maximum. The human trip’s route, transport mode, and departure conditions were not supplied.'),table(['ID','Destination','Human recorded','Google prediction','Difference','Reading'],comparison_rows,[25,122,80,72,78,95],6.5),p('B is retained in the table because it is a recorded human trip, but its selected Google destination does not reliably match the intended bus-stop side and road level. It is excluded from the charts and aggregate count. For C-M excluding B: 7 of 11 human times are at or below the selected Google prediction; four are higher. The median difference is −39 seconds; the range runs from −4 min 01 sec to +3 min 46 sec. These descriptive differences do not identify the cause of a mismatch.'),p('Why the comparison is limited','SubCustom'),p('Trips can differ because of departure time, traffic, travel mode, path, endpoint, stop access, or rounding. Google incorporates traffic and route conditions into some forecasts, while the graph’s OSRM profile times are static. The human observations are complete journeys, not measurements for each individual graph edge. A controlled comparison would record the same mode, route, start and end points, and repeated departures at matched times.')]

story += page('Phase 3 - Human and Google comparison graphs')
story += [p('Paired durations. The comparison contains the 11 destinations whose Google endpoint is treated as comparable; B is left out.'),comparison_chart('paired'),p('Each pair shows the human-recorded trip and Google’s selected upper prediction in minutes and seconds. The bars compare whole trips, not the graph’s edge weights.','SmallText')]
story += page('Phase 3 - Difference by destination')
story += [p('Difference is human-recorded duration minus Google’s upper prediction. Negative values mean the recorded trip was quicker; positive values mean it was longer.'),comparison_chart('difference'),p('The largest positive difference is Ragigudda Temple (K), +3 min 46 sec. The largest negative difference is Banashankari bus stop (H), −4 min 01 sec. The comparison does not show why those gaps occurred.','SmallText')]
story += page('Phase 3 - Human time against Google prediction')
story += [p('Each point is one comparable destination. The diagonal represents equal durations. Points above it have longer human-recorded trips; points below it have shorter recorded trips.'),comparison_chart('scatter'),p('The cluster around the equality line indicates similar rounded durations for several trips, while other destinations differ by several minutes. Google’s selected upper estimate gives a cautious reference for this comparison; it is not a measured worst case.','SmallText')]

story += page('Phase 3 - What traffic and emergency context add')
story += [p('Traffic in this study','SubCustom'),p('Google’s selected busy-period upper estimate reflects a scheduled forecast and its traffic model. The static OSRM profile data used for the teaching graph do not update with current congestion. A future traffic experiment could capture Google’s low and high estimates, then repeat human drives and record time, route, mode, and weather at the same departure windows. The present data do not support attributing a difference to traffic alone.'),p('Emergency-response interpretation','SubCustom'),p('A CAG audit of Karnataka’s 108 ambulance records reported that 52.4% of analyzed road-accident responses arrived within 15 minutes and 15.03% took more than 30 minutes. Those administrative results describe a broad set of historical incidents; they are not Bengaluru-specific estimates for these destinations and do not validate this graph. [S4]'),p('NHS England publishes category-specific response indicators, including separate mean and 90th-centile measures for the highest-priority category. This illustrates why a single route time cannot stand in for an emergency-service response measure. The definitions and service system differ from Bengaluru; they are methodological context only. [S5]'),p('A complete response interval can include call handling, triage, dispatch, vehicle availability, mobilisation, travel, and handover. This graph models only travel between selected road references. It cannot establish improved ambulance response, clinical benefit, or lives saved.'),p('Conclusion','SubCustom'),p('The learning outcome is that Dijkstra produces a reproducible optimum only relative to a clearly defined graph and objective. The route can change when distance is replaced by time or when a corridor weight changes. The Google comparison shows that actual whole-trip durations can be either shorter or longer than a scheduled prediction, while still leaving route and condition differences unresolved. The strongest next study step is a controlled classroom route-choice exercise plus matched, repeated travel observations if the project intends to study traffic.')]

story += page('Phase 4 - 180-minute learning-session plan')
story += [p('The session uses prediction, manual tracing, code verification, controlled changes, and reflection. The human journey dataset is used as context; it is not presented as participants’ route-choice or hand-calculation performance.'),table(['Minutes','Activity','Evidence to capture'],[['0-15','Introduce source A, graph weights, objectives, and question','Individual route prediction'],['15-45','Inspect 13 locations, road snaps, and directed corridor weights','Annotated network and endpoint caveats'],['45-65','Collect independent route guesses before showing Dijkstra results','Chosen route and area familiarity; no timings claimed unless collected'],['65-95','Manually trace A to C and reconstruct predecessors','Trace table and route arithmetic'],['95-120','Run the algorithm and compare distance versus modeled time','Route outputs and code-time method'],['120-140','Remove BC or triple its duration; predict then rerun','Before/after route and cost'],['140-160','Read human-versus-Google charts and traffic caveats','Evidence-based comparison statement'],['160-180','Discuss limits and write an individual reflection','Exit response and one proposed improvement']],[58,250,192],7.3),p('If collecting a classroom sample','SubCustom'),p('Use a consistent graph, weights, instructions, and destination tasks. Record participants’ guessed path, objective, familiarity, task order, and route-choice time separately. If they manually calculate Dijkstra, record completion time separately from route-choice time. Hide the algorithm answer until guesses are recorded. Use several participants or counterbalanced task order to reduce learning effects. Do not treat the already supplied actual journey times as classroom experiment timings.'),p('Suggested calculations','SubCustom'),p('For a chosen route under a specified objective: route gap (%) = 100 × (chosen cost − optimal cost) ÷ optimal cost. An optimal choice has a 0% gap. Report the participant count, median gap, and proportion with an optimal route. Keep route distance, modeled travel duration, human journey duration, decision time, manual trace time, and code runtime in separate measures.')]

story += page('Printable learning worksheet')
story += [p('Participant code: ____________________  Task: C / D / L / M / J  Objective: distance / modeled time'),p('My predicted route from A: _______________________________________________________'),p('Area familiarity: __________________  Task order: __________  Decision time (if measured): ______'),p('Initialize A=0 and all other tentative costs to infinity. At each step, settle the smallest tentative value, relax its outgoing edges, and note any improved labels and predecessors.'),table(['Step','Settled node','Cost','Improved labels / predecessors'],[['','','',''] for _ in range(12)],[40,75,75,330],7.5),p('Reconstructed route: _____________________________________________________________'),p('Chosen cost: ______________  Optimal cost: ______________  Route gap: __________'),p('Reflection','SubCustom'),p('1. Which edge changed your route prediction?<br/>2. Did the shortest route differ from the fastest modeled route? Why?<br/>3. Which missing real-world variable could change a trip?<br/>4. Did the mapped endpoint match the intended stop or entrance?<br/>5. What additional evidence would make a traffic comparison fairer?')]

story += page('Appendix C - Data definitions and source notes')
sources=[('S1','JAIN University - campus location','https://www.jainuniversity.ac.in/contact/top-indian-university-with-best-colleges-with-location-maps','Source address used for A: 44/4 District Fund Road, Jayanagara 9th Block, Bengaluru.'),('S2','OpenStreetMap contributors - map data and licence','https://www.openstreetmap.org/copyright','Mapped feature IDs, coordinates, and attribution are retained in the project source data. Licence: ODbL 1.0.'),('S3','OSRM HTTP API - table and route data','https://project-osrm.org/docs/v26.6.1/http','Table durations are seconds; route distances are metres along the selected profile routes. The public endpoint’s exact profile build and map extract are not available in the saved response.'),('S4','Comptroller and Auditor General of India - Karnataka 108 ambulance audit','https://cag.gov.in/uploads/download_audit_report/2021/Report%20No.%205%20of%202021%20Govt.%20of%20Karnataka_PA%20-062b18ae4e863e6.89140363.pdf','Primary audit source for the historical road-accident response-time figures. These are context only, not a route-model target.'),('S5','NHS England - Ambulance Quality Indicators and AmbSYS specification','https://www.england.nhs.uk/statistics/statistical-work-areas/ambulance-quality-indicators/','Official indicator definitions and response-time statistics. The service categories and jurisdiction differ from Karnataka.'),('S6','Manipal Hospitals - Jayanagar branch contact and address','https://www.manipalhospitals.com/jayanagar/contact-us/','Official branch reference used to identify M.'),('S7','Google Maps - route and busy-period predictions','https://www.google.com/maps','The report uses the saved upper end of the displayed driving forecast. Route and prediction snapshots may change; the report does not treat them as live data.')]
for key,title,url,note in sources:
    story += [p(key+' - '+title,'SubCustom'),p(f'<link href="{html.escape(url,quote=True)}" color="#00685d">Open source page</link>','SmallText'),p(note,'SmallText')]
story += [p('Terms used in the report','SubCustom'),p('<b>Teaching graph cost:</b> sum of selected directed corridor weights. <b>Distance-optimal:</b> route with least graph distance. <b>Fastest modeled route:</b> route with least static profile duration. <b>Google prediction:</b> upper end of the saved busy-period Google driving forecast. <b>Difference:</b> human journey duration minus Google prediction. <b>Road snap:</b> distance from the mapped place coordinate to the routing engine’s road reference.'),p('Data completeness','SubCustom'),p('The report contains the full location table, selected corridor weights, complete distance and duration matrices, graph outcomes, code timing measures, all simple route options for the four hospital targets, all hospital manual traces for both objectives, all human journey times, the Google upper predictions, difference calculations, controlled scenarios, and the learning materials. Human trip route, travel mode, departure time, repeat count, classroom route choices, route-choice time, and hand-calculation time were not supplied; these fields are left unclaimed.')]

def footer(canvas,doc):
    canvas.saveState();canvas.setFillColor(INK);canvas.setFont('Arial',8)
    canvas.drawString(42,24,'JAIN routing study | Educational model')
    canvas.drawRightString(553,24,str(doc.page));canvas.restoreState()
doc=SimpleDocTemplate(str(OUT/'pdf/JAIN-Routing-Report-Updated.pdf'),pagesize=(595.28,841.89),rightMargin=42,leftMargin=42,topMargin=36,bottomMargin=42,title='Every Minute Counts - JAIN Routing Study',author='JAIN routing study')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject
pdf_path=OUT/'pdf/JAIN-Routing-Report-Updated.pdf'
reader=PdfReader(str(pdf_path));writer=PdfWriter();writer.clone_document_from_reader(reader);writer.add_metadata({'/Title':'Every Minute Counts - JAIN Routing Study','/Author':'JAIN routing study'})
info=writer._info.get_object();info.pop(NameObject('/CreationDate'),None);info.pop(NameObject('/ModDate'),None)
with pdf_path.open('wb') as f: writer.write(f)
if '--report-only' in sys.argv: sys.exit(0)
renderSVG.drawToFile(graph(920,730),str(OUT/'teaching-graph.svg'))
template=(ROOT/'explorer.template.html').read_text(encoding='utf-8')
(ROOT/'index.html').write_text(template.replace('__STUDY_JSON__',json.dumps(S).replace('</','<\\/')),encoding='utf-8')
README='''# JAIN University Dijkstra routing study

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
'''
(ROOT/'README.md').write_text(README,encoding='utf-8')
with (ROOT/'data/human_input.csv').open(encoding='utf-8-sig',newline='') as f:
    reader=csv.DictReader(f);fields=reader.fieldnames;human=list(reader)
if not any(r['route'].strip() or r['participant_id'].strip() for r in human):
    with (ROOT/'data/human_input.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows({k:(task if k=='task_id' else obj if k=='objective' else '') for k in fields} for task in 'CDJLM' for obj in ('distance_m','duration_s'))
# Store source facts and metadata without redistributing complete scraped web pages.
raw_ref=json.loads((ROOT/'data/raw/reference_sources.json').read_text(encoding='utf-8'))
compact={k:({'url':v.get('metadata',{}).get('sourceURL'), 'status_code':v.get('metadata',{}).get('statusCode')} if 'markdown' in v else v) for k,v in raw_ref.items()}
(ROOT/'data/sources.json').write_text(json.dumps(compact,indent=2),encoding='utf-8')
print('Created report, explorer, vector graph and instructions.')
