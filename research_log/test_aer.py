import qiskit
from qiskit_aer import AerSimulator
qc = qiskit.QuantumCircuit(82)
qc.x(0)
sim = AerSimulator(method='statevector')
# This will probably fail:
try:
    res = sim.run(qc).result()
    print("Success!")
except Exception as e:
    print(f"Failed: {e}")
