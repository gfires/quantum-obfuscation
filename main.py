from load import load_ghz_gate
from simulation import run_baseline_simulation, run_obfuscation_simulation
from analyze import analyze_results

# ------------------------------------------------------------------
# Main execution
# ------------------------------------------------------------------
if __name__ == "__main__":
    ghz_gate = load_ghz_gate("circuits/ghz_indep_qiskit_3.qasm")

    baseline = run_baseline_simulation(num_shots=5000, gate=ghz_gate)
    static_obf = run_obfuscation_simulation(num_shots=5000, obfuscation_interval=10, gate=ghz_gate, static=True)
    dynamic_obf = run_obfuscation_simulation(num_shots=5000, obfuscation_interval=10, gate=ghz_gate, static=False)

    analyze_results(baseline, static_obf, dynamic_obf, 5000)

