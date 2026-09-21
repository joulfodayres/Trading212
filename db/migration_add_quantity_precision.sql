-- Migration: Add quantity_precision column to isins table
-- Purpose: Store T212 API's accepted quantity decimal places per ISIN
-- When T212 returns "invalid quantity precision X", we store X here

ALTER TABLE isins ADD COLUMN quantity_precision INTEGER DEFAULT 3;

-- Comment for documentation
COMMENT ON COLUMN isins.quantity_precision IS 'Number of decimal places T212 accepts for this ISIN quantity. Default 3. Updated when API returns precision error.';

-- Index for performance (though usually queried by id)
-- No index needed as we query by id or strategy_id

-- Backfill existing ISINs with default value 3
UPDATE isins SET quantity_precision = 3 WHERE quantity_precision IS NULL;

-- Make it NOT NULL after backfill
ALTER TABLE isins ALTER COLUMN quantity_precision SET NOT NULL;
