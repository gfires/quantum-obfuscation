from qiskit.qasm2 import loads

def load_ghz_gate(qasm_path: str):
    """Load a GHZ circuit from QASM, strip measurements, and return a Gate."""
    with open(qasm_path, "r") as f:
        ghz = loads(f.read())

    # Remove final measurements (required for gate conversion)
    ghz_clean = ghz.remove_final_measurements(inplace=False)

    # Convert into a Gate object (unitary subcircuit)
    ghz_gate = ghz_clean.to_gate(label="GHZ")
    return ghz_gate

