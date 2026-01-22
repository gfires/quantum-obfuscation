from qiskit import QuantumCircuit, transpile
from qiskit.qasm2 import loads
from qiskit_aer import AerSimulator
from qiskit.circuit.random import random_circuit
from collections import defaultdict
import matplotlib.pyplot as plt
import random


def load_ghz_gate(qasm_path: str):
    """Load a GHZ circuit from QASM, strip measurements, and return a Gate."""
    with open(qasm_path, "r") as f:
        ghz = loads(f.read())

    # Remove final measurements (required for gate conversion)
    ghz_clean = ghz.remove_final_measurements(inplace=False)

    # Convert into a Gate object (unitary subcircuit)
    ghz_gate = ghz_clean.to_gate(label="GHZ")
    return ghz_gate


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
    res = defaultdict(int)
    recovered_res = defaultdict(int)
    num_trials = num_shots // obfuscation_interval

    for _ in range(num_trials):
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

        for outcome, count in counts.items():
            res[outcome] += count

            # Extract GHZ bits based on start index
            bits = outcome[::-1]
            ghz_bits = ''.join(
                bits[start_idx + i] for i in range(gate.num_qubits)
            )
            recovered_res[ghz_bits] += count

    print(f"\n=== {'Static' if static else 'Dynamic'} Obfuscation Recovered Counts ===")
    for key in sorted(recovered_res):
        print(f"{key}: {recovered_res[key]}")

    return dict(res)


def total_variation_distance(counts: dict, baseline_counts: dict, num_shots: int) -> float:
    """
    Calculate total variation distance between observed distribution and baseline.
    TVD = 0.5 * sum(|p(x) - q(x)|) for all possible outcomes.
    """
    # Get all possible keys from both distributions
    all_keys = set(counts.keys()) | set(baseline_counts.keys())

    # Calculate TVD
    tvd = 0.0
    for key in all_keys:
        p = counts.get(key, 0) / num_shots
        q = baseline_counts.get(key, 0) / num_shots
        tvd += abs(p - q)

    return 0.5 * tvd


def dominant_state_percentile(counts: dict, num_shots: int, top_n: int = 2) -> float:
    """
    Calculate the percentage of shots in the top N most frequent states.
    """
    sorted_counts = sorted(counts.values(), reverse=True)
    top_counts = sum(sorted_counts[:top_n])
    return (top_counts / num_shots) * 100


def analyze_results(baseline: dict, static_obf: dict, dynamic_obf: dict, num_shots: int):
    """
    Analyze and plot results from the three experiments.
    Generates bar charts for TVD and dominant state percentile, plus overlaid PDF.
    """
    experiments = ['Baseline', 'Static', 'Dynamic']

    # Calculate metrics
    tvd_values = [
        0.0,  # Baseline vs itself
        total_variation_distance(static_obf, baseline, num_shots),
        total_variation_distance(dynamic_obf, baseline, num_shots)
    ]

    dominant_values = [
        dominant_state_percentile(baseline, num_shots),
        dominant_state_percentile(static_obf, num_shots),
        dominant_state_percentile(dynamic_obf, num_shots)
    ]

    # Create figure with 2 subplots
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))

    # Plot 1: TVD bar chart
    tvd_labels = [f'{exp}: {val:.3f}' for exp, val in zip(experiments, tvd_values)]
    axes[0].bar(tvd_labels, tvd_values, color=['green', 'orange', 'red'])
    axes[0].set_ylabel('Total Variation Distance')
    axes[0].set_title('TVD from Baseline Distribution')
    axes[0].set_ylim(0, 1)

    # Plot 2: Dominant state percentile bar chart
    dom_labels = [f'{exp}: {val:.1f}%' for exp, val in zip(experiments, dominant_values)]
    axes[1].bar(dom_labels, dominant_values, color=['green', 'orange', 'red'])
    axes[1].set_ylabel('Percentage (%)')
    axes[1].set_title('Top-2 Dominant States Percentile')
    axes[1].set_ylim(0, 100)

    plt.tight_layout()
    plt.savefig('obfuscation_analysis.png', dpi=150)
    plt.show()

    # Print metrics
    print("\n=== Analysis Results ===")
    for i, exp in enumerate(experiments):
        print(f"{exp}:")
        print(f"  TVD from baseline: {tvd_values[i]:.4f}")
        print(f"  Top-2 dominant states: {dominant_values[i]:.2f}%")


# ------------------------------------------------------------------
# Main execution
# ------------------------------------------------------------------
if __name__ == "__main__":
    ghz_gate = load_ghz_gate("ghz_indep_qiskit_3.qasm")

    baseline = run_baseline_simulation(num_shots=5000, gate=ghz_gate)
    static_obf = run_obfuscation_simulation(num_shots=5000, obfuscation_interval=10, gate=ghz_gate, static=True)
    dynamic_obf = run_obfuscation_simulation(num_shots=5000, obfuscation_interval=10, gate=ghz_gate, static=False)

    analyze_results(baseline, static_obf, dynamic_obf, 5000)

