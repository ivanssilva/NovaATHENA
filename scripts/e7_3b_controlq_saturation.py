"""E7.3b synthetic ControlQ saturation (not observed OoO timing)."""
from collections import deque
from itertools import product
from pathlib import Path
import csv, json

def simulate(arrivals, lc, cc, period, policy, lr):
    assert policy in ('drop','backpressure') and min(lc,cc,period,lr)>0
    pending=deque(enumerate(t for t,n in enumerate(arrivals) for _ in range(n)))
    learn,control=deque(),deque()
    accepted=dropped=completed=blocked=full=peak_l=peak_c=occ=latency=cycle=0
    while pending or learn or control:
        if cycle%period==0 and control:
            _,born=control.popleft(); completed+=1; latency+=cycle-born+1
        for _ in range(lr):
            if not learn or len(control)==cc: break
            control.append(learn.popleft())
        stalled=False
        while pending and pending[0][1]<=cycle:
            if len(learn)<lc: learn.append(pending.popleft()); accepted+=1
            elif policy=='drop': pending.popleft(); dropped+=1
            else: stalled=True; break
        blocked+=int(stalled); full+=int(len(control)==cc)
        occ+=len(control); peak_l=max(peak_l,len(learn)); peak_c=max(peak_c,len(control))
        cycle+=1
        assert cycle<100000 and len(learn)<=lc and len(control)<=cc
    assert accepted==completed and completed+dropped==sum(arrivals)
    return dict(offered=sum(arrivals),accepted=accepted,completed=completed,dropped=dropped,
        cycles=cycle,blocked_cycles=blocked,full_control_cycles=full,peak_learn=peak_l,
        peak_control=peak_c,mean_control_occupancy=occ/cycle,
        control_full_fraction=full/cycle,mean_completion_latency=latency/completed if completed else 0)

def main():
    assert simulate([1],1,1,1,'backpressure',1)['completed']==1
    a=simulate([4]*12,2,1,4,'backpressure',2)
    assert a['completed']==48 and a['dropped']==0 and a['blocked_cycles']>0 and a['full_control_cycles']>0
    b=simulate([4]*12,2,1,4,'drop',2)
    assert b['dropped']>0 and b['completed']+b['dropped']==48
    out=Path('e7-3b-results');out.mkdir(exist_ok=True)
    fields=['pattern','policy','learn_cap','control_cap','service_period','learn_rate',
        'offered','accepted','completed','dropped','cycles','blocked_cycles','full_control_cycles',
        'peak_learn','peak_control','mean_control_occupancy','control_full_fraction','mean_completion_latency']
    count=0
    with (out/'controlq_saturation.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for (name,arr),policy,lc,cc,period,lr in product(
            [('burst',[4]*12),('sparse',[int(i%4==0) for i in range(48)])],
            ('drop','backpressure'),(1,4),(1,2,4),(1,2,4),(1,2)):
            r=simulate(arr,lc,cc,period,policy,lr)
            w.writerow(dict(pattern=name,policy=policy,learn_cap=lc,control_cap=cc,
                service_period=period,learn_rate=lr,**r))
            count+=1
    assert count==144
    (out/'manifest.json').write_text(json.dumps(dict(kind='synthetic_parameter_sweep',
        scenarios=count,service='one ControlQ retirement every service_period cycles; no bypass',
        limitation='not real OoO traces; not CPU performance prediction'),indent=2))
    print(f'E7_3B_SYNTHETIC_PASS scenarios {count} controlq_saturation verified',flush=True)

if __name__=='__main__': main()
