import json
import os
import sys
import numpy as np
from datetime import datetime, timezone, timedelta
from qiskit_ibm_runtime import QiskitRuntimeService

# Configuration
BACKEND_NAME = "ibm_fez"
TARGET_TIMESTAMP = datetime.fromisoformat("2026-05-01T21:27:09.866499").replace(tzinfo=timezone.utc)

def main():
    print("Connecting to Qiskit Runtime Service...")
    try:
        token = os.environ.get("IBM_QUANTUM_TOKEN")
        if token:
            service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token)
        else:
            service = QiskitRuntimeService()
    except Exception as e:
        print(f"Failed to authenticate: {e}")
        print("Please ensure your IBM Quantum credentials are saved or IBM_QUANTUM_TOKEN is set.")
        sys.exit(1)
        
    print(f"Searching for historical jobs on {BACKEND_NAME} around {TARGET_TIMESTAMP}...")
    
    # Fetch recent jobs on the backend
    try:
        jobs = service.jobs(backend_name=BACKEND_NAME, limit=50, created_before=TARGET_TIMESTAMP + timedelta(hours=2))
    except Exception as e:
        print(f"Failed to retrieve jobs: {e}")
        sys.exit(1)
        
    valid_jobs = []
    for j in jobs:
        # SamplerV2 jobs usually have program_id == 'sampler'
        if getattr(j, 'program_id', '') == 'sampler':
            valid_jobs.append(j)
            
    # Sort by absolute time difference from TARGET_TIMESTAMP
    valid_jobs.sort(key=lambda j: abs((j.creation_date - TARGET_TIMESTAMP).total_seconds()))
    
    # Take the top 8
    target_jobs = valid_jobs[:8]
    # Sort them back chronologically
    target_jobs.sort(key=lambda j: j.creation_date)
    
    if len(target_jobs) < 8:
        print(f"Could not find 8 jobs. Found only {len(target_jobs)}")
        print("HISTORICAL_CALIBRATION_UNAVAILABLE")
        sys.exit(1)
        
    print(f"Found 8 target jobs.")
    
    provenance_data = []
    raw_calibration_data = []
    
    table_rows = []
    
    for i, job in enumerate(target_jobs):
        job_id = job.job_id() if callable(job.job_id) else job.job_id
        creation_date = job.creation_date
        print(f"\nProcessing Job {i+1}/8: {job_id} executed at {creation_date}")
        
        pubs = job.inputs.get('pubs', [])
        if not pubs:
            print("No pubs found in job.")
            continue
            
        pub = pubs[0]
        if isinstance(pub, tuple):
            circuit = pub[0]
        else:
            circuit = getattr(pub, "circuit", None)
            if circuit is None:
                circuit = pub[0]
                
        # Active physical qubits and couplers
        active_qubits = set()
        active_couplers = set()
        
        for inst in circuit.data:
            if inst.operation.name == 'barrier':
                continue
            
            phys_qargs = []
            for q in inst.qubits:
                try:
                    idx = circuit.find_bit(q).index
                    phys_qargs.append(idx)
                    active_qubits.add(idx)
                except:
                    pass
            
            if len(phys_qargs) == 2:
                q0, q1 = phys_qargs
                active_couplers.add((min(q0, q1), max(q0, q1)))
                
        print(f"  Active Qubits: {len(active_qubits)}")
        print(f"  Active Couplers: {len(active_couplers)}")
        
        print(f"  Retrieving backend calibration snapshot...")
        try:
            backend = service.backend(BACKEND_NAME)
            props = backend.properties(datetime=creation_date)
        except Exception as e:
            print(f"  Error retrieving properties: {e}")
            props = None
            
        if not props:
            print("  HISTORICAL_CALIBRATION_UNAVAILABLE")
            sys.exit(1)
            
        snapshot_time = props.last_update_date
        time_diff = abs((snapshot_time - creation_date).total_seconds())
        print(f"  Snapshot timestamp: {snapshot_time}")
        print(f"  Time difference: {time_diff:.1f} seconds")
        
        provenance_data.append({
            "job_id": job_id,
            "execution_timestamp": creation_date.isoformat(),
            "snapshot_timestamp": snapshot_time.isoformat(),
            "time_difference_seconds": time_diff
        })
        
        t1s = []
        t2s = []
        readouts = []
        gate1qs = []
        gate2qs = []
        
        for q in active_qubits:
            try:
                t1s.append(props.t1(q))
                t2s.append(props.t2(q))
                readouts.append(props.readout_error(q))
                for g in ['sx', 'x', 'rz']:
                    try:
                        gate1qs.append(props.gate_error(g, [q]))
                        break
                    except:
                        pass
            except:
                pass
                
        for (q0, q1) in active_couplers:
            found = False
            for g in ['ecr', 'cx', 'cz']:
                try:
                    gate2qs.append(props.gate_error(g, [q0, q1]))
                    found = True
                    break
                except:
                    pass
            if not found:
                for g in ['ecr', 'cx', 'cz']:
                    try:
                        gate2qs.append(props.gate_error(g, [q1, q0]))
                        break
                    except:
                        pass
                        
        med_t1 = np.median(t1s) * 1e6 if t1s else 0
        med_t2 = np.median(t2s) * 1e6 if t2s else 0
        med_readout = np.median(readouts) if readouts else 0
        med_1q = np.median(gate1qs) if gate1qs else 0
        med_2q = np.median(gate2qs) if gate2qs else 0
        
        raw_calibration_data.append({
            "job_id": job_id,
            "median_t1_us": med_t1,
            "median_t2_us": med_t2,
            "median_readout_error": med_readout,
            "median_1q_error": med_1q,
            "median_2q_error": med_2q
        })
        
        row = f"{i+1} & {med_t1:.1f} & {med_t2:.1f} & {med_1q:.2e} & {med_2q:.2e} & {med_readout:.2e} \\\\"
        table_rows.append(row)
        
    with open("hardware_provenance.json", "w") as f:
        json.dump(provenance_data, f, indent=2)
        
    with open("hardware_calibration_raw.json", "w") as f:
        json.dump(raw_calibration_data, f, indent=2)
        
    print("\n" + "="*70)
    print("LaTeX Table for paper:")
    print("\\begin{table}[htbp]")
    print("\\caption{Median hardware calibration metrics for the active physical qubits during each execution.}")
    print("\\label{tab:calibration}")
    print("\\begin{center}")
    print("\\begin{tabular}{lccccc}")
    print("\\toprule")
    print("\\textbf{Run} & \\textbf{T1 ($\\mu$s)} & \\textbf{T2 ($\\mu$s)} & \\textbf{1Q Error} & \\textbf{2Q Error} & \\textbf{Readout Error} \\\\")
    print("\\midrule")
    for r in table_rows:
        print(r)
    print("\\bottomrule")
    print("\\end{tabular}")
    print("\\end{center}")
    print("\\end{table}")
    print("="*70)

if __name__ == "__main__":
    main()
