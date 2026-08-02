import numpy as np

class GateLevelSimulator:
    def __init__(self, num_qubits):
        # State representation:
        # For computational basis: bool True/False
        # For Fourier basis: phase angle (float) in [0, 1) where 1 means 2*pi
        # We track if a qubit is in the Fourier domain
        self.num_qubits = num_qubits
        self.bits = np.zeros(num_qubits, dtype=bool)
        self.phases = np.zeros(num_qubits, dtype=float)
        self.is_fourier = np.zeros(num_qubits, dtype=bool)

    def set_input(self, bitstring):
        """Set classical basis state from a binary string like '101'."""
        assert len(bitstring) <= self.num_qubits
        # Initialize all to 0 computational basis
        self.bits.fill(False)
        self.phases.fill(0.0)
        self.is_fourier.fill(False)
        for i, bit in enumerate(reversed(bitstring)):
            if bit == '1':
                self.bits[i] = True

    def run(self, qc):
        """Execute unrolled qiskit circuit."""
        from qiskit.circuit.library import standard_gates
        
        # We assume qubits are mapped 1-to-1 to their indices (0 to num_qubits-1)
        for instruction in qc.data:
            gate = instruction.operation
            qargs = [qc.find_bit(q).index for q in instruction.qubits]
            
            name = gate.name
            if name == 'x':
                assert not self.is_fourier[qargs[0]], "X on Fourier qubit"
                self.bits[qargs[0]] = not self.bits[qargs[0]]
            elif name == 'cx':
                c, t = qargs[0], qargs[1]
                if self.is_fourier[c] or self.is_fourier[t]:
                    print(f"FAILED on cx: c={c} (f={self.is_fourier[c]}), t={t} (f={self.is_fourier[t]}), bits={[self.bits[i] for i in qargs]}")
                assert not self.is_fourier[c] and not self.is_fourier[t]
                if self.bits[c]:
                    self.bits[t] = not self.bits[t]
            elif name == 'ccx':
                c1, c2, t = qargs[0], qargs[1], qargs[2]
                assert not self.is_fourier[c1] and not self.is_fourier[c2] and not self.is_fourier[t]
                if self.bits[c1] and self.bits[c2]:
                    self.bits[t] = not self.bits[t]
            elif name == 'swap':
                t1, t2 = qargs[0], qargs[1]
                assert not self.is_fourier[t1] and not self.is_fourier[t2]
                self.bits[t1], self.bits[t2] = self.bits[t2], self.bits[t1]
            elif name == 'h':
                # H transforms |0> to + phase, |1> to 0.5 phase
                t = qargs[0]
                if not self.is_fourier[t]:
                    self.is_fourier[t] = True
                    self.phases[t] = 0.5 if self.bits[t] else 0.0
                    self.bits[t] = False
                else:
                    self.is_fourier[t] = False
                    # Collapse from Fourier back to computational basis
                    # phase must be approx 0.0 or 0.5
                    val = self.phases[t] % 1.0
                    if abs(val) < 1e-6 or abs(val - 1.0) < 1e-6:
                        self.bits[t] = False
                    elif abs(val - 0.5) < 1e-6:
                        self.bits[t] = True
                    else:
                        raise ValueError(f"Invalid phase for inverse H collapse: {val}")
                    self.phases[t] = 0.0
            elif name == 'cp':
                # Controlled phase rotation
                c, t = qargs[0], qargs[1]
                if not self.is_fourier[t] and not self.is_fourier[c]:
                    # Both classical: it just adds a global phase to the |11> state. Ignore it.
                    pass
                else:
                    if not self.is_fourier[t] and self.is_fourier[c]: c, t = t, c
                    if self.is_fourier[c] or not self.is_fourier[t]:
                        print(f"FAILED on cp: inst={instruction} c={c} (f={self.is_fourier[c]}), t={t} (f={self.is_fourier[t]})")
                    assert not self.is_fourier[c], f"Control must be classical. Inst: {instruction}"
                    assert self.is_fourier[t], "Target must be in Fourier domain"
                    if self.bits[c]:
                        theta = float(gate.params[0])
                        self.phases[t] = (self.phases[t] + theta / (2 * np.pi)) % 1.0
            elif name == 'ccp':
                c1, c2, t = qargs[0], qargs[1], qargs[2]
                assert not self.is_fourier[c1] and not self.is_fourier[c2], "Controls must be classical"
                assert self.is_fourier[t], "Target must be in Fourier domain"
                if self.bits[c1] and self.bits[c2]:
                    theta = float(gate.params[0])
                    self.phases[t] = (self.phases[t] + theta / (2 * np.pi)) % 1.0
            elif name == 'p':
                t = qargs[0]
                assert self.is_fourier[t]
                theta = float(gate.params[0])
                self.phases[t] = (self.phases[t] + theta / (2 * np.pi)) % 1.0
            elif name == 'u':
                t = qargs[0]
                assert not self.is_fourier[t]
                theta = float(gate.params[0])
                if abs(theta - np.pi) < 1e-6:
                    self.bits[t] = not self.bits[t]
                elif abs(theta) < 1e-6:
                    pass
                else:
                    raise NotImplementedError(f"U gate with theta={theta} not supported")
            elif name == 'barrier':
                pass
            else:
                raise NotImplementedError(f"Gate {name} not supported by custom statevector simulator")
                
    def get_boolean_result(self, bit_indices):
        """Extract the integer value from a set of computational basis qubits."""
        val = 0
        for i, bit_idx in enumerate(bit_indices):
            assert not self.is_fourier[bit_idx], f"Qubit {bit_idx} is still in Fourier domain"
            if self.bits[bit_idx]:
                val += (1 << i)
        return val

