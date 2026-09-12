# Phase 2 Validation Report

## Dataset Summary

* Raw tweets processed: 2,811,774
* AmazonHelp tweets: 169,840
* Reconstructed conversations: 82,556

## Validation Results

* [PASS] No duplicate conversation IDs.
* [PASS] No duplicate root tweets.
* [PASS] Every conversation contains AmazonHelp.
* [PASS] No empty conversation text.
* [PASS] Conversations start with customer whenever possible.

## Conversation Statistics

| Metric           | Value |
| ---------------- | ----: |
| Average messages |  4.53 |
| Median messages  |     3 |
| Maximum messages |   448 |
| Minimum messages |     2 |

Generated automatically by `reconstruct_conversations.py`.
