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

```text
nectarlite/
├── __init__.py
├── api.py
├── account.py
├── comment.py
├── vote.py
├── haf.py
├── memo.py
├── stream.py
├── transaction.py
├── chain.py
├── exceptions.py
└── crypto/
    ├── __init__.py
    ├── keys.py
    ├── memo.py
    ├── aes.py
    ├── base58.py
    ├── bip32.py
    ├── bip38.py
    └── ecdsa.py
```

## Phase 1: Core Components

- [x] **API Communication:** Implement the core logic for making API calls to Hive nodes.
- [x] **Cryptography:** Port over the essential cryptography modules from `nectargraphenebase`.
- [x] **Transaction Building:** Implement the logic for creating and signing transactions.
- [x] **Chain Data:** Implement basic data structures for interacting with the blockchain.

## Phase 2: High-Level Abstractions

- [x] **Account:** Create a simple `Account` class with dynamic, auto-refreshing properties.
- [x] **Block:** Create a simple `Block` class.
- [x] **Amount:** Create a simple `Amount` class.
- [x] **Asset:** Create a simple `Asset` class.
- [x] **Comment:** Create a `Comment` class with dynamic, auto-refreshing properties.
- [x] **Vote:** Create a `Vote` class with dynamic, auto-refreshing properties.
- [x] **HAF:** Create a `HAF` class for interacting with the Hive Account Feed.

## Phase 3: Refinement and Testing

- [x] **Unit Tests:** Write comprehensive unit tests for all components.
- [x] **Documentation:** Write clear and concise documentation, including a `README.md` and example usage scripts.
- [x] **Linting and Formatting:** Ensure the code adheres to PEP 8 and other best practices.

## Phase 4: User-Friendly Scripting Enhancements

Inspired by hive-nectar, add select common features for easier script-writing.

- [x] **Wallet Class:** Add a simple in-memory `Wallet` for key management.
- [x] **Dynamic, Auto-Refreshing Objects:** The `Account`, `Comment`, and `Vote` classes now automatically fetch their data.
- [x] **Key Utilities:** Helper functions for WIF keys and memo encryption/decryption.
- [x] **API Robustness:** Enhance `Api` with basic node failover.

- [x] **Common Operation Helpers:** Pre-built classes/methods for frequent Hive actions:
  - [x] `TransferOp`: HIVE/HBD transfers with optional encrypted memo.
  - [x] `VoteOp`: Up/down-vote on content with percent weight.
  - [x] `CommentOp`: Post articles, comments, or replies.
  - [x] `FollowOp`: See extended version in Phase 5. (See `examples/account_follow.py` for usage.)

- [x] **Examples:** Expand `examples/` with scripts for all major features.

## Phase 5: Advanced Features

- [x] **Event Listener:** Implement a real-time event listener for streaming blocks and operations.

- [ ] **Common Operation Helpers (Extended):** Inspired by lighthive:
  - [x] `FollowOp`: Follow/unfollow/ignore/unignore accounts (implemented via `Account` helpers and supporting tests/examples).
  - [x] **Account Helper Methods:** Add utility methods for:
    - [x] Reputation calculation
    - [x] Voting power calculation with regeneration
    - [x] Resource Credits (RC) information
  - [x] Read-only API helpers covering dynamic globals, feed history, reward funds, RC metrics, market ticker, ranked posts.
  - [ ] Broaden helper coverage to additional endpoints (witness info, proposal feeds, market depth).

- [ ] **Advanced Node Management:** Enhance `Api` with:
  - [ ] Latency testing and intelligent node selection
  - [ ] Circuit breaker pattern for temporarily excluding failing nodes
  - [ ] Node performance metrics

- [ ] **Batch Transaction Processing:** Support for batched API calls for better performance.

- [ ] **Broader Operation Support:** Add helper classes for less common operations (e.g., witness voting, account recovery).
- [ ] **Validation:** Add more robust validation for transaction parameters and data types.

## Phase 6: Alpha Feature Completeness

- [ ] **Operation Coverage Expansion:** Implement serializers and helpers for additional core Hive operations (`comment`, `comment_options`, `delete_comment`, `claim_reward_balance`, `transfer_to_vesting`, `withdraw_vesting`, `delegate_vesting_shares`, `set_withdraw_vesting_route`, `account_update`).
- [ ] **Account Workflow Helpers:** Extend `account.Account` with ready-to-sign helpers for rewards claiming, power up/down flows, delegation management, witness voting, and escrow or proposal interactions leveraging the expanded operations.
- [ ] **Wallet Ergonomics Enhancements:** Improve the in-memory `wallet.Wallet` with multi-account utilities, optional passphrase gating, and ergonomic key loading APIs while honoring the "No Keystorage" principle.
- [ ] **Async API Client:** Provide an asyncio-native `AsyncApi` (e.g., via `httpx`/`aiohttp`) to pair with `stream.AsyncStream` without thread hopping and enable async transaction workflows.
- [ ] **Higher-Level Modules:** Introduce lightweight facades for markets, witnesses, proposals, notifications, and RC analytics comparable to coverage in `helpers.py` but focused on common scripting scenarios.
- [ ] **Testing & Documentation:** Add regression tests for new serializers/helpers, broadcast smoke tests, and expand docs/examples to cover posting, voting, power up/down, delegation, and reward claims using the new APIs.
