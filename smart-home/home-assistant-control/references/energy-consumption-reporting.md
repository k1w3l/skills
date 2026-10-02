# Home Assistant energy-consumption reports

Use this reference when Sr. Kiwel asks for recurring energy/consumption reports from Home Assistant.

## Report requirements captured from user preference

- Report should resemble the existing battery report style: clear header, divider lines, concise executive summary, individual sections, and actionable/operational language.
- Tariff for estimates: `R$ 1,03/kWh` unless the user gives a newer tariff.
- Daily report covers **yesterday's** consumption, not current day-to-date consumption.
- On the first day of each month, include a complete report for the **previous month**.
- Separate results into:
  - **Consumo geral**: total/house/grid/general meters when available.
  - **Consumo individual**: per-device/per-circuit energy entities.
- Calculate cost as `consumption_kwh * tariff` and label it as an estimate.
- Deliver recurring reports to Telegram by default.

## Implementation pattern

1. Read `HASS_URL` / `HOME_ASSISTANT_URL` and `HASS_TOKEN` / `HA_TOKEN` / `HOME_ASSISTANT_TOKEN` from the environment or `~/.hermes/.env`; never print the token.
2. Discover candidate sensors via `/api/states`:
   - `entity_id` starts with `sensor.`
   - `unit_of_measurement` is `kWh`, `Wh`, or `MWh`
   - `device_class` is absent or `energy`
   - numeric current state
   - exclude power/current/voltage/battery/cost/tariff sensors.
3. For each candidate, query `/api/history/period/<start>?filter_entity_id=<id>&end_time=<end>&significant_changes_only=0`.
4. For total/total_increasing meters, compute consumption by summing positive deltas. If a meter resets, add the current reading after reset when positive.
5. Convert units to kWh before summing:
   - `Wh / 1000`
   - `kWh` unchanged
   - `MWh * 1000`
6. Classify general meters with names/IDs containing terms such as `total`, `geral`, `casa`, `house`, `home`, `grid`, `rede`, `medidor`, `consumo_total`, `energia_total`; everything else is individual.
7. If no general meter exists, use the sum of individual consumptions as the general reference and state that no total entity was found.
8. Schedule as a script-only Hermes cron (`no_agent=True`) so the script prints the exact Telegram message:
   - `schedule: 0 12 * * *` for ~09:00 in America/Sao_Paulo when scheduler uses UTC.
   - `deliver: telegram`.

## Pitfalls

- Do not use a sensor's current state as daily/monthly consumption unless it is a utility meter for that exact period. Prefer history deltas for arbitrary reporting windows.
- Do not count `W`, `A`, `V`, battery, tariff, cost, or price sensors as energy consumption.
- Home Assistant history can be large; query one entity and one period at a time and keep cron output user-facing.
- Avoid internal cron/job IDs, script paths, or debug details in Telegram output unless troubleshooting is explicitly requested.
