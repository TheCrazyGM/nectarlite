# Nectarlite Roadmap

This document outlines the development plan for `nectarlite`, a lightweight Python library for the Hive blockchain.

## Guiding Principles

- **Lightweight:** No extra fluff. Only the essentials for interacting with the Hive blockchain.
- **Library, not a framework:** `nectarlite` should be a library that can be easily integrated into other Python applications.
- **No CLI:** No command-line interface.
- **No Hivesigner:** No integration with Hivesigner.
- **No SQL:** No database integration.
- **No Keystorage:** No on-disk key storage. Keys should be handled in memory.

## Project Structure

```
nectarlite/
├── __init__.py
├── api.py
├── transaction.py
├── chain.py
├── exceptions.py
└── crypto/
    ├── __init__.py
    ├── aes.py
    ├── base58.py
    ├── bip32.py
    ├── bip38.py
    └── ecdsa.py
```

## Phase 1: Core Components

- [x] **API Communication:** Implement the core logic for making API calls to Hive nodes.
  - [x] `api.py`: Create a class for making RPC calls.
  - [x] `exceptions.py`: Define custom exception classes.
- [x] **Cryptography:** Port over the essential cryptography modules from `nectargraphenebase`.
  - [x] `crypto/aes.py`: AES encryption/decryption for memos.
  - [x] `crypto/base58.py`: Base58 encoding/decoding for keys.
  - [x] `crypto/bip32.py`: BIP32 for hierarchical deterministic keys.
  - [x] `crypto/bip38.py`: BIP38 for encrypted keys.
  - [x] `crypto/ecdsa.py`: ECDSA for signing and verifying transactions.
- [x] **Transaction Building:** Implement the logic for creating and signing transactions.
  - [x] `transaction.py`: Create a `Transaction` class.
  - [x] `transaction.py`: Implement methods for adding operations to a transaction.
  - [x] `transaction.py`: Implement methods for signing transactions.
- [x] **Chain Data:** Implement basic data structures for interacting with the blockchain.
  - [x] `chain.py`: Create a `Chain` class to hold chain-specific data (e.g., chain ID, prefix).
  - [x] `__init__.py`: Expose the core classes.

## Phase 2: High-Level Abstractions

- [x] **Account:** Create a simple `Account` class.
- [x] **Block:** Create a simple `Block` class.
- [x] **Amount:** Create a simple `Amount` class.
- [x] **Asset:** Create a simple `Asset` class.

## Phase 3: Refinement and Testing

- [x] **Unit Tests:** Write comprehensive unit tests for all components.
- [x] **Documentation:** Write clear and concise documentation.
- [x] **Linting and Formatting:** Ensure the code adheres to PEP 8 and other best practices.

## Phase 4: User-Friendly Scripting Enhancements

Inspired by hive-nectar, add select common features for easier script-writing (e.g., high-level ops like transfers and votes). Keep it optional and lightweight—users can still build custom ops using core classes.

- [x] **Wallet Class:** Add a simple in-memory `Wallet` for key management (load keys by name from WIF, select for signing). Implemented in `src/nectarlite/wallet.py`.

- [ ] **Common Operation Helpers:** Pre-built classes/methods for frequent Hive actions (append to `Transaction` easily):
  - [ ] `TransferOp`: HIVE/HBD transfers with optional encrypted memo.
  - [ ] `VoteOp`: Up/down-vote on content with percent weight.
  - [ ] `CommentOp`: Post articles, comments, or replies.
  - [ ] `FollowOp`: Follow/unfollow accounts.

- [ ] **Key Utilities:** Helper functions in `crypto/` or `utils/`:
  - [ ] Import/validate WIF keys.
  - [ ] Memo encryption/decryption (using public/private keys).

- [ ] **API Robustness:** Enhance `Api`:
  - [ ] Node failover (try secondary nodes on failure).
  - [ ] Optional query caching (e.g., for chain params).

- [ ] **Validation:** Basic checks (e.g., valid account name format, amount precision).

- [ ] **Examples:** Expand `examples/` with new scripts (e.g., simple voter, transfer bot skeleton).
