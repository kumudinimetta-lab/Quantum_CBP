import qiskit
from qiskit_aer import AerSimulator
qc = qiskit.QuantumCircuit(82)
qc.x(0)
qc.save_statevector()
sim = AerSimulator(method='statevector')
try:
    res = sim.run(qc).result()
    print("Success!", len(res.get_statevector()))
except Exception as e:
    print(f"Failed: {e}")
