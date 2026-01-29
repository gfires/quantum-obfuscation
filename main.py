from load import load_gate
from simulation import run_baseline_simulation, run_obfuscation_simulation
from analyze import analyze_results

# ------------------------------------------------------------------
# Main execution
# ------------------------------------------------------------------
if __name__ == "__main__":
    NUM_SHOTS = 5000

    # Load gate blocks
    ghz_gate = load_gate("circuits/ghz_indep_qiskit_3.qasm")
    print("Loaded GHZ gate")
    w_gate = load_gate("circuits/wstate_indep_qiskit_3.qasm")
    print("Loaded W-state gate")
    grover_gate = load_gate("circuits/grover-noancilla_indep_qiskit_3.qasm")
    print("Loaded Grover gate")
    qft_gate = load_gate("circuits/qft_indep_qiskit_3.qasm")
    print("Loaded QFT gate")

    # Compute expected distributions
    gates = [(ghz_gate, "ghz_gate"), (w_gate, "w_gate"), (grover_gate, "grover_gate"), (qft_gate, "qft_gate")]
    ghz_expected = {'0000000000': NUM_SHOTS / 2, '0000111000': NUM_SHOTS / 2}
    w_expected = {'0000100000': NUM_SHOTS / 3, '0000010000': NUM_SHOTS / 3, '0000001000': NUM_SHOTS / 3}
    grover_expected = {'0000111000': NUM_SHOTS}
    
    qft_expected = {}
    for b4 in ['0', '1']:
        for b5 in ['0', '1']:
            for b6 in ['0', '1']:
                key = f"0000{b4}{b5}{b6}000"
                qft_expected[key] = NUM_SHOTS / 8
    
    expected_distributions = {
        "ghz_gate": ghz_expected,
        "w_gate": w_expected,
        "grover_gate": grover_expected,
        "qft_gate": qft_expected,
    }

    # Run simulations and analyze results for each gate
    for gate, name in gates:
        print(f"\n=== Running simulations for gate: {name} ===")
        print(gate)
        baseline = run_baseline_simulation(num_shots=NUM_SHOTS, gate=gate)
        static_obf, static_recovered = run_obfuscation_simulation(num_shots=NUM_SHOTS, obfuscation_interval=10, gate=gate, static=True)
        dynamic_obf, dynamic_recovered = run_obfuscation_simulation(num_shots=NUM_SHOTS, obfuscation_interval=10, gate=gate, static=False)

        analyze_results(name, expected_distributions[name], baseline, static_obf, static_recovered, dynamic_obf, dynamic_recovered, NUM_SHOTS)

