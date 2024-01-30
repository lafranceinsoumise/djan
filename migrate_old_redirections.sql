INSERT INTO djan_redirection
(
  site_id,
  short_url,
  destination_url,
  http_status,
  params_mode,
  unique_counter_mode,
  counter,
  unique_counter
)
SELECT
    site_id,
    SUBSTR(old_path, 2),
    new_path,
    302,
    'DEFAULT',
    'NONE',
    0,
    0
FROM django_redirect
WHERE true
ON CONFLICT (site_id) DO NOTHING;
