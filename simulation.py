from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit.circuit.random import random_circuit
from collections import defaultdict
import matplotlib.pyplot as plt
import random


def build_circuit_with_gate(
    num_qubits: int,
    gate,
    start_index: int,
    measure: bool = True
) -> QuantumCircuit:
    """
    Build a quantum circuit with a specified gate block inserted at a given start index.
    Args:
        num_qubits (int): Total number of qubits in the circuit.
        gate (Gate): The gate block to insert.
        start_index (int): The starting qubit index to insert the gate block.
        measure (bool): Whether to include measurements at the end.
    Returns:
        QuantumCircuit: The constructed quantum circuit.
    """
    if start_index < 0 or start_index + gate.num_qubits > num_qubits:
        raise ValueError("Gate block does not fit within the circuit.")

    # Allocate classical bits only if measuring
    qc = QuantumCircuit(num_qubits, num_qubits if measure else 0)

    # Build the circuit
    qubits = list(range(start_index, start_index + gate.num_qubits))
    qc.append(gate, qubits)

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


def run_baseline_simulation(num_shots: int, gate):
    """
    Run a baseline simulation with the gate block in a fixed position.
    Args:
        num_shots (int): Number of shots for the simulation.
        gate (Gate): The gate block to insert.
    Returns:
        dict: Measurement counts from the baseline simulation.
    """
    qc = build_circuit_with_gate(num_qubits=10, gate=gate, start_index=3)
    counts_baseline = simulate_circuit(qc, shots=num_shots)
    print("\n=== Baseline Counts ===")
    for key in sorted(counts_baseline.keys()):
        print(f"{key}: {counts_baseline[key]}")
    return counts_baseline


def run_obfuscation_simulation(
    num_shots: int,
    obfuscation_interval: int,
    gate,
    static: bool,
):
    """
    Run an obfuscation simulation with random circuits before and after the gate block.
    Args:
        num_shots (int): Total number of shots for the simulation.
        obfuscation_interval (int): Number of shots per obfuscation trial.
        gate (Gate): The gate block to insert.
        static (bool): If True, use a fixed start index; if False, randomize it.
    Returns:
        dict: Measurement counts from the obfuscation simulation.
    """
    res = defaultdict(int)
    recovered_res = defaultdict(int)
    num_trials = num_shots // obfuscation_interval

    for trial_idx in range(num_trials):
        # Retry mechanism for valid circuit generation (random generation will occasionally break transpiler)
        max_retries = 10

        for attempt in range(max_retries):
            try:
                start_idx = 3 if static else random.randint(0, 7)

                # Build circuit with gate at random/fixed position
                qc = build_circuit_with_gate(
                    num_qubits=10,
                    gate=gate,
                    start_index=start_idx,
                    measure=False,
                )

                # Random circuit BEFORE gate
                if start_idx > 0:
                    rand_top = random_circuit(
                        num_qubits=start_idx,
                        depth=4,
                        max_operands=2,
                    )
                    qc.compose(rand_top, qubits=list(range(start_idx)), inplace=True)

                # Random circuit AFTER gate
                end_idx = start_idx + gate.num_qubits
                if end_idx < 10:
                    rand_bottom = random_circuit(
                        num_qubits=10 - end_idx,
                        depth=4,
                        max_operands=2,
                    )
                    qc.compose(rand_bottom, qubits=list(range(end_idx, 10)), inplace=True)

                qc.measure_all()
                counts = simulate_circuit(qc, shots=obfuscation_interval)

                # Success - break out of retry loop
                break

            except BaseException as e:
                print(f"[DEBUG] Exception in trial {trial_idx + 1}, attempt {attempt + 1}: {type(e).__name__}")
                print(f"[DEBUG] Error at: {str(e)[:150]}")
                if attempt == max_retries - 1:
                    print(f"\n[ERROR] Failed to generate valid circuit after {max_retries} attempts in trial {trial_idx + 1}")
                    print(f"[ERROR] Final error details: {e}")
                    raise
                # Retry with new random circuit
                print(f"[DEBUG] Retrying... (attempt {attempt + 2}/{max_retries})")
                continue

        # Process results after successful simulation
        for outcome, count in counts.items():
            res[outcome] += count

            # Extract result bits based on start index
            bits = outcome[::-1]
            result_bits = ''.join(
                bits[start_idx + i] for i in range(gate.num_qubits)
            )
            recovered_res['0000' + result_bits + '000'] += count

    print(f"\n=== {'Static' if static else 'Dynamic'} Obfuscation Recovered Counts ===")
    for key in sorted(recovered_res):
        print(f"{key}: {recovered_res[key]}")

    return (dict(res), dict(recovered_res))