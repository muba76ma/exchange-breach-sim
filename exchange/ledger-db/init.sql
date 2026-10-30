CREATE TABLE balances (
  id SERIAL PRIMARY KEY,
  user_id TEXT NOT NULL,
  asset TEXT NOT NULL,
  amount NUMERIC(20,8) NOT NULL DEFAULT 0
);

INSERT INTO balances (user_id, asset, amount) VALUES
  ('alice', 'BTC',   1.0),
  ('alice', 'ETH',   10.0),
  ('bob',   'USDT',  50000);
