from qiskit import QuantumCircuit
from qiskit.qasm2 import loads

def load_gate(qasm_path: str):
    qc = QuantumCircuit.from_qasm_file(qasm_path)
    # Remove this line: qc = qc.decompose()
    qc = qc.remove_final_measurements(inplace=False)
    
    clean = QuantumCircuit(qc.num_qubits)
    for instr, qargs, _ in qc.data:
        clean.append(instr, [clean.qubits[qc.find_bit(q).index] for q in qargs])
    
    return clean.to_gate()
