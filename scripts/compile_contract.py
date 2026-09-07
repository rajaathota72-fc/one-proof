"""Compiles contracts/Verification.sol, writes ABI + bytecode to build/. Run before deploy_contract.py."""
import json
import os
import solcx

CONTRACT_PATH = os.path.join(os.path.dirname(__file__), "..", "contracts", "Verification.sol")
BUILD_DIR = os.path.join(os.path.dirname(__file__), "..", "build")

SOLC_VERSION = "0.8.19"


def main():
    solcx.install_solc(SOLC_VERSION)
    solcx.set_solc_version(SOLC_VERSION)

    with open(CONTRACT_PATH) as f:
        source = f.read()

    compiled = solcx.compile_source(
        source,
        output_values=["abi", "bin"],
        solc_version=SOLC_VERSION,
    )
    contract_id, contract_interface = list(compiled.items())[0]

    os.makedirs(BUILD_DIR, exist_ok=True)
    with open(os.path.join(BUILD_DIR, "Verification.abi.json"), "w") as f:
        json.dump(contract_interface["abi"], f, indent=2)
    with open(os.path.join(BUILD_DIR, "Verification.bin"), "w") as f:
        f.write(contract_interface["bin"])

    print("Compiled. ABI + bytecode written to build/")


if __name__ == "__main__":
    main()
