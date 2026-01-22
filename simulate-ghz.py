from qiskit import QuantumCircuit, transpile
from qiskit.qasm2 import loads
from qiskit_aer import AerSimulator
import matplotlib.pyplot as plt
import numpy as np
import random
from collections import defaultdict
from qiskit.circuit.random import random_circuit


def load_ghz_gate(qasm_path: str):
    """Load a GHZ circuit from QASM, strip measurements, and return a Gate."""
    with open(qasm_path, "r") as f:
        ghz = loads(f.read())

    # Remove final measurements (required for gate conversion)
    ghz_clean = ghz.remove_final_measurements(inplace=False)

    # Convert into a Gate object (unitary subcircuit)
    ghz_gate = ghz_clean.to_gate(label="GHZ")
    return ghz_gate


def build_circuit_with_gate(num_qubits: int, gate, start_index: int = 0, measure: bool = True):
    """
    Build a quantum circuit with a specified gate block inserted at a given start index.
    Args:
        num_qubits (int): Total number of qubits in the circuit.
        gate (Gate): The gate block to insert.
        start_index (int): The starting qubit index for the gate block.
        measure (bool): Whether to add measurements on all qubits.
    Returns:
        QuantumCircuit: The constructed quantum circuit.
    """
    qc = QuantumCircuit(num_qubits, num_qubits)
    # Determine which qubits the gate block goes on
    qubits = list(range(start_index, start_index + gate.num_qubits))
    # Insert gate block
    qc.append(gate, qubits)
    # Add measurements on all qubits if requested
    if measure:
        qc.measure(range(num_qubits), range(num_qubits))
    return qc


def simulate_circuit(qc, shots: int):
    """
    Simulate the given quantum circuit and return the measurement counts.
    Args:
        qc (QuantumCircuit): The quantum circuit to simulate.
        shots (int): Number of shots for the simulation.
    Returns:
        dict: Measurement counts."""
    sim = AerSimulator()
    compiled = transpile(qc, sim)
    result = sim.run(compiled, shots=shots).result()
    return result.get_counts()


def run_baseline_simulation(num_shots: int = 1000, gate = None):
    """
    Run a baseline simulation with the gate block in a fixed position.
    Args:
        num_shots (int): Number of shots for the simulation.
        gate (Gate): The gate block to insert.
    """
    qc = build_circuit_with_gate(num_qubits=10, gate=gate, start_index=3)
    counts_baseline = simulate_circuit(qc, shots=num_shots)
    print(counts_baseline)
    return counts_baseline


def run_obfuscation_simulation(num_shots: int = 1000, obfuscation_interval: int = 10, gate = None, static: bool = False):
    """
    Run an obfuscation simulation with random circuits added before and after the gate block.
    Args:
        num_shots (int): Total number of shots for the simulation.
        obfuscation_interval (int): Number of shots per obfuscation iteration.
        gate (Gate): The gate block to insert.
        static (bool): If True, use a fixed start index; if False, randomize start index each iteration.
    """
    res = defaultdict(int)
    for _ in range(0, num_shots, obfuscation_interval):
        start_idx = 3 if static else random.randint(0, 7)
        # Build circuit without measurements first
        qc = build_circuit_with_gate(num_qubits=10, gate=gate, start_index=start_idx, measure=False)
        # Add random circuits on qubits before gate
        if (start_idx > 0):
            rand_top = random_circuit(start_idx, 4)
            qc.append(rand_top, list(range(0, start_idx)))
        # Add random circuits on qubits after gate
        if (start_idx + gate.num_qubits < 10):
            rand_bottom = random_circuit(10 - (start_idx + gate.num_qubits), 4)
            qc.append(rand_bottom, list(range(start_idx + gate.num_qubits, 10)))
        # Add measurements after all gates
        qc.measure(range(10), range(10))
        # Simulate and add counts to results
        counts = simulate_circuit(qc, shots=obfuscation_interval)
        for key in counts:
            res[key] += counts[key]
    final_counts = dict(res)
    print(final_counts)
    return final_counts


# ------------------------------------------------------------------
# Main execution
# ------------------------------------------------------------------
if __name__ == "__main__":
    ghz_gate = load_ghz_gate("ghz_indep_qiskit_3.qasm")
    run_baseline_simulation(num_shots=1000, gate=ghz_gate)
    run_obfuscation_simulation(num_shots=1000, obfuscation_interval=10, gate=ghz_gate, static=True)
    run_obfuscation_simulation(num_shots=1000, obfuscation_interval=10, gate=ghz_gate, static=False)
    
