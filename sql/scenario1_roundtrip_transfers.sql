-- ============================================================================
-- SCENARIO 1: ROUND-TRIP TRANSFERS WITHIN 24-HOUR WINDOW (10% AMOUNT TOLERANCE)
-- Description:
-- Detects instances where Account A sends money to Account B, and Account B
-- sends a similar amount (within 10%) back to Account A within 24 hours.
-- Identifies potential payment reversals, check-kiting, or money laundering loops.
-- ============================================================================

-- Drop existing table if present
DROP TABLE IF EXISTS transactions;

-- 1. Table Schema
CREATE TABLE transactions (
    transaction_id VARCHAR(20) PRIMARY KEY,
    sender_account_id VARCHAR(20) NOT NULL,
    receiver_account_id VARCHAR(20) NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    transaction_timestamp TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'COMPLETED'
);

-- 2. Seed Data
-- Cases:
-- TXN_001 & TXN_002: $1,000 sent, $950 returned after 4 hours (5% diff, 4h) -> MATCH
-- TXN_003 & TXN_004: $500 sent, $500 returned after 18 hours (0% diff, 18h) -> MATCH
-- TXN_005 & TXN_006: $1,000 sent, $850 returned after 2 hours (15% diff) -> NO MATCH (>10%)
-- TXN_007 & TXN_008: $2,000 sent, $2,000 returned after 28 hours -> NO MATCH (>24h)
-- TXN_009: $3,000 sent, no return transfer -> NO MATCH
-- TXN_010 & TXN_011: $1,500 sent, $1,600 returned after 6.5 hours (6.67% diff, 6.5h) -> MATCH

INSERT INTO transactions (transaction_id, sender_account_id, receiver_account_id, amount, transaction_timestamp, status) VALUES
('TXN_001', 'ACC_101', 'ACC_202', 1000.00, '2024-05-10 09:00:00', 'COMPLETED'),
('TXN_002', 'ACC_202', 'ACC_101',  950.00, '2024-05-10 13:00:00', 'COMPLETED'),

('TXN_003', 'ACC_303', 'ACC_404',  500.00, '2024-05-11 08:30:00', 'COMPLETED'),
('TXN_004', 'ACC_404', 'ACC_303',  500.00, '2024-05-12 02:30:00', 'COMPLETED'),

('TXN_005', 'ACC_505', 'ACC_606', 1000.00, '2024-05-12 10:00:00', 'COMPLETED'),
('TXN_006', 'ACC_606', 'ACC_505',  850.00, '2024-05-12 12:00:00', 'COMPLETED'),

('TXN_007', 'ACC_707', 'ACC_808', 2000.00, '2024-05-13 09:00:00', 'COMPLETED'),
('TXN_008', 'ACC_808', 'ACC_707', 2000.00, '2024-05-14 13:00:00', 'COMPLETED'),

('TXN_009', 'ACC_909', 'ACC_111', 3000.00, '2024-05-14 15:00:00', 'COMPLETED'),

('TXN_010', 'ACC_222', 'ACC_333', 1500.00, '2024-05-15 10:00:00', 'COMPLETED'),
('TXN_011', 'ACC_333', 'ACC_222', 1600.00, '2024-05-15 16:30:00', 'COMPLETED');

-- 3. Target Query (SQLite / ANSI Compatible)
SELECT 
    t1.transaction_id AS leg1_txn_id,
    t1.sender_account_id AS account_a,
    t1.receiver_account_id AS account_b,
    t1.amount AS leg1_amount,
    t1.transaction_timestamp AS leg1_timestamp,
    t2.transaction_id AS leg2_txn_id,
    t2.amount AS leg2_amount,
    t2.transaction_timestamp AS leg2_timestamp,
    ROUND(ABS(t2.amount - t1.amount), 2) AS amount_diff,
    ROUND(ABS(t2.amount - t1.amount) * 100.0 / t1.amount, 2) AS pct_diff,
    ROUND((JULIANDAY(t2.transaction_timestamp) - JULIANDAY(t1.transaction_timestamp)) * 24.0, 2) AS hours_between
FROM transactions t1
INNER JOIN transactions t2
    ON t1.sender_account_id = t2.receiver_account_id
   AND t1.receiver_account_id = t2.sender_account_id
WHERE t2.transaction_timestamp > t1.transaction_timestamp
  AND (JULIANDAY(t2.transaction_timestamp) - JULIANDAY(t1.transaction_timestamp)) * 24.0 <= 24.0
  AND ABS(t2.amount - t1.amount) <= (0.10 * t1.amount)
  AND t1.status = 'COMPLETED'
  AND t2.status = 'COMPLETED'
ORDER BY t1.transaction_timestamp;
