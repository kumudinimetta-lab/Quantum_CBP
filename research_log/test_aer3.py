import qiskit
from qiskit_aer import AerSimulator
qc = qiskit.QuantumCircuit(82)
qc.x(0)
qc.x(1)
qc.ccx(0, 1, 2)
qc.measure_all()
sim = AerSimulator()
try:
    res = sim.run(qc).result()
    counts = res.get_counts()
    print("Success!", counts)
except Exception as e:
    print(f"Failed: {e}")
