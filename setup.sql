-- Create SEARCH_ON column if not exists
ALTER TABLE IF EXISTS smoothies.public.fruit_options
ADD COLUMN IF NOT EXISTS SEARCH_ON STRING;

-- Update some initial known mappings
UPDATE smoothies.public.fruit_options SET SEARCH_ON = 'Apples' WHERE FRUIT_NAME = 'Apples';
UPDATE smoothies.public.fruit_options SET SEARCH_ON = 'Blueberries' WHERE FRUIT_NAME = 'Blueberries';
UPDATE smoothies.public.fruit_options SET SEARCH_ON = 'Jackfruit' WHERE FRUIT_NAME = 'Jack Fruit';
UPDATE smoothies.public.fruit_options SET SEARCH_ON = 'Raspberries' WHERE FRUIT_NAME = 'Raspberries';
UPDATE smoothies.public.fruit_options SET SEARCH_ON = 'Strawberries' WHERE FRUIT_NAME = 'Strawberries';

-- Fill in blank SEARCH_ON values with FRUIT_NAME
UPDATE smoothies.public.fruit_options
SET SEARCH_ON = FRUIT_NAME
WHERE SEARCH_ON IS NULL;
