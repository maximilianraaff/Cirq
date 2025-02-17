# Copyright 2021 The Cirq Developers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import pytest

import cirq
import cirq_google as cg
import cirq_google.engine.engine_validator as engine_validator

SERIALIZABLE_GATE_DOMAIN = {
    cirq.X: 1,
    cirq.Y: 1,
    cirq.Z: 1,
    cirq.S: 1,
    cirq.T: 1,
    cirq.CZ: 2,
}


def test_validate_gate_set():
    circuit = cirq.testing.random_circuit(
        cirq.GridQubit.rect(5, 5),
        n_moments=10,
        op_density=1.0,
        gate_domain=SERIALIZABLE_GATE_DOMAIN,
    )

    engine_validator.validate_gate_set(
        [circuit] * 5, [{}] * 5, 1000, cg.FSIM_GATESET, max_size=100000
    )

    with pytest.raises(RuntimeError, match='Program too long'):
        engine_validator.validate_gate_set(
            [circuit] * 10, [{}] * 10, 1000, cg.FSIM_GATESET, max_size=100000
        )

    with pytest.raises(RuntimeError, match='Program too long'):
        engine_validator.validate_gate_set(
            [circuit] * 5, [{}] * 5, 1000, cg.FSIM_GATESET, max_size=10000
        )


def test_create_gate_set_validator():
    circuit = cirq.testing.random_circuit(
        cirq.GridQubit.rect(4, 4),
        n_moments=10,
        op_density=1.0,
        gate_domain=SERIALIZABLE_GATE_DOMAIN,
    )

    smaller_size_validator = engine_validator.create_gate_set_validator(max_size=20000)
    smaller_size_validator([circuit] * 2, [{}] * 2, 1000, cg.FSIM_GATESET)
    with pytest.raises(RuntimeError, match='Program too long'):
        smaller_size_validator([circuit] * 5, [{}] * 5, 1000, cg.FSIM_GATESET)
    larger_size_validator = engine_validator.create_gate_set_validator(max_size=50000)
    larger_size_validator([circuit] * 5, [{}] * 5, 1000, cg.FSIM_GATESET)


def test_validate_for_engine():
    circuit = cirq.testing.random_circuit(
        cirq.GridQubit.rect(5, 5),
        n_moments=10,
        op_density=1.0,
        gate_domain=SERIALIZABLE_GATE_DOMAIN,
    )
    long_circuit = cirq.Circuit([cirq.X(cirq.GridQubit(0, 0))] * 10001)

    with pytest.raises(RuntimeError, match='Provided circuit exceeds the limit'):
        engine_validator.validate_for_engine([long_circuit], [{}], 1000)

    with pytest.raises(RuntimeError, match='the number of requested total repetitions'):
        engine_validator.validate_for_engine([circuit], [{}], 10_000_000)

    with pytest.raises(RuntimeError, match='the number of requested total repetitions'):
        engine_validator.validate_for_engine([circuit] * 6, [{}] * 6, 1_000_000)

    with pytest.raises(RuntimeError, match='the number of requested total repetitions'):
        engine_validator.validate_for_engine(
            [circuit] * 6, [{}] * 6, [4_000_000, 2_000_000, 1, 1, 1, 1]
        )


def test_validate_for_engine_no_meas():
    circuit = cirq.Circuit(cirq.X(cirq.GridQubit(0, 0)))
    with pytest.raises(RuntimeError, match='Code must measure at least one qubit.'):
        engine_validator.validate_for_engine([circuit] * 6, [{}] * 6, 1_000)
