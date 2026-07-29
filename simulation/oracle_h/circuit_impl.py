from qiskit import QuantumRegister, QuantumCircuit
from qiskit.circuit import Gate
import math

class OracleHCircuit:
    def __init__(self, W_max, V_max, Z_LB):
        self.W_max = W_max
        self.V_max = V_max
        self.Z_LB = Z_LB
        self.k = math.ceil(2 * math.log2(W_max))
        
        # Define logical register sizes
        self.sz_v_s_scaled = math.ceil(math.log2(V_max + 1)) + self.k
        
        # Thapliyal divider requires equal-width operands.
        # We zero-pad the divisor and remainder to match the dividend's width (N).
        self.N_div = self.sz_v_s_scaled 
        self.sz_w_s = self.N_div
        self.sz_e_s = self.sz_v_s_scaled
        self.sz_rem = self.N_div
        
        self.sz_W_res = math.ceil(math.log2(W_max + 1))
        self.sz_frac_val = self.sz_W_res + self.sz_e_s
        self.sz_V_int_scaled = math.ceil(math.log2(Z_LB + 2)) + self.k
        self.sz_cmp_flag = 1
        
        # Define ancilla register sizes (derived from primary sources)
        self.sz_anc_mul = 1            # VBE: 1 reused carry ancilla for plain multiplication
        self.sz_anc_add = 0            # Draper QFT: 0 ancilla
        
        # Pre-compute classical threshold T
        self.T = math.floor(Z_LB * (2**self.k) - (2**self.k) / W_max)
        
    def build_circuit(self):
        # Initialize logical quantum registers
        q_v_s_scaled = QuantumRegister(self.sz_v_s_scaled, 'v_s_scaled')
        q_w_s = QuantumRegister(self.sz_w_s, 'w_s')
        q_e_s = QuantumRegister(self.sz_e_s, 'e_s')
        q_rem = QuantumRegister(self.sz_rem, 'rem')
        q_W_res = QuantumRegister(self.sz_W_res, 'W_res')
        q_frac_val = QuantumRegister(self.sz_frac_val, 'frac_val')
        q_V_int_scaled = QuantumRegister(self.sz_V_int_scaled, 'V_int_scaled')
        q_cmp_flag = QuantumRegister(self.sz_cmp_flag, 'cmp_flag')
        
        # Initialize ancilla quantum registers
        q_anc_mul = QuantumRegister(self.sz_anc_mul, 'anc_mul')
        
        qc = QuantumCircuit(
            q_v_s_scaled, q_w_s, q_e_s, q_rem, q_W_res, q_frac_val, 
            q_V_int_scaled, q_cmp_flag, q_anc_mul
        )
        
        # 1. Thapliyal Restoring Division: e_s, rem = v_s_scaled / w_s
        div_gate = Gate('Thapliyal_Div', num_qubits=self.sz_v_s_scaled + self.sz_w_s + self.sz_e_s + self.sz_rem, params=[])
        qc.append(div_gate, q_v_s_scaled[:] + q_w_s[:] + q_e_s[:] + q_rem[:])
        
        # 2. Vedral-Barenco-Ekert (VBE) Multiplier: frac_val = W_res * e_s
        mul_gate = Gate('VBE_Mul', num_qubits=self.sz_W_res + self.sz_e_s + self.sz_frac_val + self.sz_anc_mul, params=[])
        qc.append(mul_gate, q_W_res[:] + q_e_s[:] + q_frac_val[:] + q_anc_mul[:])
        
        # 3. Draper QFT Adder: V_int_scaled += frac_val
        add_gate = Gate('Draper_Add', num_qubits=self.sz_frac_val + self.sz_V_int_scaled, params=[])
        qc.append(add_gate, q_frac_val[:] + q_V_int_scaled[:])
        
        # 4. Classical Comparator: cmp_flag = (V_int_scaled <= T)
        cmp_gate = Gate(f'Compare_LE_{self.T}', num_qubits=self.sz_V_int_scaled + self.sz_cmp_flag, params=[])
        qc.append(cmp_gate, q_V_int_scaled[:] + q_cmp_flag[:])
        
        return qc, {
            'logical': qc.num_qubits - self.sz_anc_mul,
            'ancilla': self.sz_anc_mul,
            'total': qc.num_qubits
        }

    def verify_arithmetic_formula_only(self, v_s, w_s, W_res, V_int):
        """
        Verifies the mathematical ARITHMETIC FORMULA only (the exact integer manipulations
        and truncation errors that the quantum circuit is specified to execute).
        This does NOT verify actual gate-level execution, as full gate-level decomposition
        is deferred.
        """
        v_s_scaled = v_s * (2**self.k)
        e_s = v_s_scaled // w_s
        rem = v_s_scaled % w_s
        frac_val = W_res * e_s
        V_int_scaled = V_int * (2**self.k)
        Z_scaled = V_int_scaled + frac_val
        flag = Z_scaled <= self.T
        return {
            'Z_scaled': Z_scaled,
            'T': self.T,
            'flag': flag,
            'e_s_real': e_s / (2**self.k),
            'Z_real': Z_scaled / (2**self.k)
        }

if __name__ == '__main__':
    configs = [
        (4, 15, 15, 10),
        (6, 31, 31, 20),
        (8, 63, 63, 40)
    ]
    print('--- Register Counts (Derived) ---')
    for m, W_max, V_max, Z_LB in configs:
        oracle = OracleHCircuit(W_max, V_max, Z_LB)
        qc, counts = oracle.build_circuit()
        print(f'm={m} (W_max={W_max}): Logical = {counts["logical"]}, Ancilla = {counts["ancilla"]} (Mul:{oracle.sz_anc_mul}), Total = {counts["total"]}')
    
    print('\n--- Basic Sanity Checks (Arithmetic Formula Verification) ---')
    # Instance 1: The tight true worst-case degenerate from Step 2
    W_max, V_max, Z_LB = 15, 15, 10
    oracle = OracleHCircuit(W_max, V_max, Z_LB)
    res = oracle.verify_arithmetic_formula_only(v_s=10, w_s=15, W_res=12, V_int=2)
    print(f'Sanity Check 1 (Exact Degenerate): Z_LB={Z_LB}, T={res["T"]}, Z_scaled={res["Z_scaled"]}, Pruned={res["flag"]}')
    
    # Instance 2: Clearly suboptimal (Z_LB - 1)
    res2 = oracle.verify_arithmetic_formula_only(v_s=10, w_s=15, W_res=12, V_int=1)
    print(f'Sanity Check 2 (Suboptimal): Z_LB={Z_LB}, T={res2["T"]}, Z_scaled={res2["Z_scaled"]}, Pruned={res2["flag"]}')
    
    # Instance 3: Clearly optimal (Z_LB + 1)
    res3 = oracle.verify_arithmetic_formula_only(v_s=10, w_s=15, W_res=12, V_int=3)
    print(f'Sanity Check 3 (Optimal): Z_LB={Z_LB}, T={res3["T"]}, Z_scaled={res3["Z_scaled"]}, Pruned={res3["flag"]}')
