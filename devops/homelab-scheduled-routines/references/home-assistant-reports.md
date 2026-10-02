# Home Assistant recurring reports

Use this reference when a Tiberius-owned routine reports Home Assistant batteries or energy consumption.

## Battery reports

- Read `HASS_URL` and `HASS_TOKEN` (or the existing supported aliases) from the runtime environment or the managed environment file; never print or persist the value.
- Query `/api/states` and include `device_class: battery` sensors plus entities whose `entity_id` or friendly name contains `bateria`/`battery` and whose unit is `%`.
- Exclude battery state, health, temperature, power, voltage, and current sensors; maintain explicit exclusions for named noisy entities and dedicated personal-device monitors to prevent duplicate alerts.
- Separate numeric readings into critical (≤5%), attention (6–20%), and normal (>20%); list unavailable or non-numeric entities separately.
- Use a per-entity cooldown state only for alerts. A daily report always prints the current table and must not consume alert cooldown state.

## Energy reports

- Discover `sensor.*` entities with `kWh`, `Wh`, or `MWh` units and an energy-compatible device/state class; reject power, current, voltage, battery, tariff, cost, and price sensors.
- Query Home Assistant history for the requested local period and compute positive deltas. Treat a decreasing counter as a reset and add only the positive post-reset reading.
- Report yesterday by default; include the previous-month close on the first day of the month; estimate cost with the configured tariff and label it as an estimate.
- Classify household/grid/general meters separately from per-device meters. A device named `Servidor Energia total` or `Nobreak Mesa Energia total` is still individual; do not classify every label containing `total` as the household total.
- If no general meter exists, state that the sum of individual meters is being used as the reference instead of presenting it as a measured household total.

## Handoff and verification

- Create one script-only job per report in the owning profile and pause the equivalent old-profile report before enabling the new one.
- Confirm the saved `next_run_at` in `America/Sao_Paulo`; do not blindly convert a local scheduler schedule to UTC.
- Run the report and an alert check with state writes disabled where supported, inspect for false positives, compile the implementation, and run the scheduler doctor.
- Do not send a Telegram test merely to prove the job exists; a live script run plus saved job state is the safe pre-delivery verification unless an immediate notification is explicitly requested.
