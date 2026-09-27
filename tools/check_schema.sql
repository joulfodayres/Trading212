-- Verificar schema da tabela app_parameters
SELECT 
  column_name, 
  data_type, 
  is_nullable,
  column_default
FROM information_schema.columns 
WHERE table_name = 'app_parameters'
ORDER BY ordinal_position;

-- Verificar dados
SELECT * FROM app_parameters;
