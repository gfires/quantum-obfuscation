from qiskit import QuantumCircuit, transpile
from qiskit.qasm2 import loads
from qiskit_aer import AerSimulator
import matplotlib.pyplot as plt


# ------------------------------------------------------------------
# Load and prepare GHZ subcircuit
# ------------------------------------------------------------------
def load_ghz_gate(qasm_path: str):
    """Load a GHZ circuit from QASM, strip measurements, and return a Gate."""
    with open(qasm_path, "r") as f:
        ghz = loads(f.read())

    # Remove final measurements (required for gate conversion)
    ghz_clean = ghz.remove_final_measurements(inplace=False)

    # Convert into a Gate object (unitary subcircuit)
    ghz_gate = ghz_clean.to_gate(label="GHZ")
    return ghz_gate


# ------------------------------------------------------------------
# Build a top-level circuit with GHZ placed at chosen qubits
# ------------------------------------------------------------------
def build_circuit_with_ghz(num_qubits: int, ghz_gate, start_index: int = 0):
    """
    Create a circuit of size num_qubits and insert GHZ at start_index.
    """
    qc = QuantumCircuit(num_qubits)

    # Determine which qubits the GHZ block goes on
    ghz_qubits = list(range(start_index, start_index + ghz_gate.num_qubits))

    # Insert GHZ block
    qc.append(ghz_gate, ghz_qubits)

    # Measure after all operations
    qc.measure_all()
    return qc


# ------------------------------------------------------------------
# Simulate and return counts
# ------------------------------------------------------------------
def simulate_circuit(qc, shots: int = 1000):
    sim = AerSimulator()
    compiled = transpile(qc, sim)
    result = sim.run(compiled, shots=shots).result()
    return result.get_counts()

# ------------------------------------------------------------------
# Run baseline simulation
# ------------------------------------------------------------------
def run_baseline_simulation(qc):
    counts_baseline = simulate_circuit(qc)
    print(counts_baseline)

# ------------------------------------------------------------------
# Run in-place obfuscation simulation
# ------------------------------------------------------------------


# --------------------------------------
# Main execution
# ------------------------------------------------------------------
if __name__ == "__main__":
    ghz_gate = load_ghz_gate("ghz_indep_qiskit_3.qasm")
    qc = build_circuit_with_ghz(num_qubits=10, ghz_gate=ghz_gate, start_index=3)
    run_baseline_simulation(qc)
