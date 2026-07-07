import json
from collections import Counter

def check_smoke_test():
    with open('quantum_walk_results_smoke.json', 'r') as f:
        data = json.load(f)
        
    records = data['records']
    
    print(f"Attempted: {len(records)}")
    
    # Status counter
    status_counts = Counter(r['status'] for r in records)
    print("\n=== STATUS TABLE ===")
    for status, count in status_counts.items():
        print(f"{status}: {count}")
        
    assert len(records) == 60, "Should have exactly 60 records"
    
    # Verifications
    for r in records:
        if r['status'] == 'COMPLETED':
            m = r['m']
            d_bound = r['d_bound']
            t_lp = r['T_LP']
            assert d_bound == m
            assert t_lp <= (2**(m+1)) - 1
            assert r['correctness'] is True
            
    print("\nAll verifications passed!")

if __name__ == "__main__":
    check_smoke_test()
