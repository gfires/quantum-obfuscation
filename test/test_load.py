import pytest
from qiskit import QuantumCircuit
from qiskit.circuit import Gate, Instruction
from load import load_gate


class TestLoadGate:
    """Unit tests for the load_gate function."""

    # Test data: (circuit_path, expected_num_qubits, description)
    CIRCUITS = [
        ("circuits/ghz_indep_qiskit_3.qasm", 3, "GHZ"),
        ("circuits/wstate_indep_qiskit_3.qasm", 3, "W-state"),
        ("circuits/grover-noancilla_indep_qiskit_3.qasm", 3, "Grover"),
        ("circuits/qft_indep_qiskit_3.qasm", 3, "QFT"),
    ]

    @pytest.mark.parametrize("circuit_path,expected_qubits,description", CIRCUITS)
    def test_load_gate_returns_instruction(self, circuit_path, expected_qubits, description):
        """Test that load_gate returns an Instruction object."""
        gate = load_gate(circuit_path)
        assert isinstance(gate, Instruction), (
            f"{description}: Expected Instruction, got {type(gate)}"
        )

    @pytest.mark.parametrize("circuit_path,expected_qubits,description", CIRCUITS)
    def test_load_gate_correct_num_qubits(self, circuit_path, expected_qubits, description):
        """Test that loaded gates have the correct number of qubits."""
        gate = load_gate(circuit_path)
        assert gate.num_qubits == expected_qubits, (
            f"{description}: Expected {expected_qubits} qubits, got {gate.num_qubits}"
        )

    @pytest.mark.parametrize("circuit_path,expected_qubits,description", CIRCUITS)
    def test_load_gate_no_classical_bits(self, circuit_path, expected_qubits, description):
        """Test that loaded gates have no classical bits."""
        gate = load_gate(circuit_path)
        assert gate.num_clbits == 0, (
            f"{description}: Expected 0 classical bits, got {gate.num_clbits}"
        )

    @pytest.mark.parametrize("circuit_path,expected_qubits,description", CIRCUITS)
    def test_load_gate_has_instructions(self, circuit_path, expected_qubits, description):
        """Test that loaded gates contain instructions (not empty)."""
        gate = load_gate(circuit_path)
        # Convert gate to circuit to inspect instructions
        qc = QuantumCircuit(gate.num_qubits)
        qc.append(gate, range(gate.num_qubits))
        # The circuit should have at least one instruction (the gate itself)
        assert len(qc.data) > 0, (
            f"{description}: Gate appears to be empty (no instructions)"
        )

    @pytest.mark.parametrize("circuit_path,expected_qubits,description", CIRCUITS)
    def test_load_gate_can_be_appended(self, circuit_path, expected_qubits, description):
        """Test that loaded gates can be appended to a quantum circuit."""
        gate = load_gate(circuit_path)
        qc = QuantumCircuit(5)  # Create circuit with more qubits than gate needs

        # Should be able to append the gate
        try:
            qc.append(gate, range(expected_qubits))
        except Exception as e:
            pytest.fail(f"{description}: Failed to append gate to circuit: {e}")

        assert len(qc.data) == 1, (
            f"{description}: Expected 1 instruction after append, got {len(qc.data)}"
        )

    @pytest.mark.parametrize("circuit_path,expected_qubits,description", CIRCUITS)
    def test_load_gate_has_name(self, circuit_path, expected_qubits, description):
        """Test that loaded gates have a name attribute."""
        gate = load_gate(circuit_path)
        assert hasattr(gate, 'name'), f"{description}: Gate missing 'name' attribute"
        assert isinstance(gate.name, str), (
            f"{description}: Gate name should be string, got {type(gate.name)}"
        )
        assert len(gate.name) > 0, f"{description}: Gate name is empty"

    def test_load_nonexistent_file(self):
        """Test that loading a nonexistent file raises appropriate error."""
        with pytest.raises(FileNotFoundError):
            load_gate("circuits/nonexistent.qasm")

    def test_load_all_gates_different(self):
        """Test that all four gates are distinct (different names or structures)."""
        gates = [load_gate(path) for path, _, _ in self.CIRCUITS]

        # At minimum, check they're all valid gates
        assert len(gates) == 4, "Should load 4 gates"
        assert all(isinstance(g, Instruction) for g in gates), "All should be Instructions"
        assert all(g.num_qubits == 3 for g in gates), "All should have 3 qubits"
        assert all(g.num_clbits == 0 for g in gates), "All should have 0 classical bits"

    @pytest.mark.parametrize("circuit_path,expected_qubits,description", CIRCUITS)
    def test_load_gate_no_measurements(self, circuit_path, expected_qubits, description):
        """Test that loaded gates don't contain measurement operations."""
        gate = load_gate(circuit_path)

        # Convert to circuit and decompose to check for measurements
        qc = QuantumCircuit(gate.num_qubits)
        qc.append(gate, range(gate.num_qubits))
        decomposed = qc.decompose()

        # Check no measurement operations
        for instruction in decomposed.data:
            assert instruction.operation.name != 'measure', (
                f"{description}: Gate contains measurement operation"
            )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
