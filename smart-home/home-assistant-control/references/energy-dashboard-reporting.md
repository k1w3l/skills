# Home Assistant energy dashboards

Use this reference when a user asks for an annual/month-to-date HTML energy dashboard, charts, rankings, or a scheduled dashboard attachment alongside a daily briefing.

## Data model

1. Fix the editorial timezone (for Sr. Kiwel, `America/Sao_Paulo`) and the target year.
2. Discover only energy entities (`sensor.*`, numeric `Wh`/`kWh`/`MWh`, compatible energy/state class). Exclude power, current, voltage, battery, tariff, cost, and price sensors.
3. Query each entity's history once from one day before the year's first local midnight through the current local time. The extra day provides a carry-in reading for the January boundary.
4. Convert deltas to kWh and assign each positive delta to the local month of its ending sample. Treat a decreasing counter as a reset and add the post-reset reading; never add negative deltas.
5. Persist a JSON model containing year, coverage, tariff, monthly totals/costs/daily averages, entity totals/monthly values, top entity, peak month, and `data_available`/`status` per month.
6. Distinguish missing history from measured zero: show `sem dados` for months with no samples, not `0 kWh`. Keep the current month marked `parcial` when it has data.

## HTML contract

Generate a self-contained HTML file with inline CSS, JavaScript, and SVG/DOM charts so it works without a CDN:

- `lang="pt-BR"`, viewport meta, responsive single-column fallback below tablet width;
- KPI cards for accumulated kWh, estimated cost, monthly average, peak month, and top entity;
- monthly bar chart, gauge/indicator, top-entity horizontal bars, and an accessible month table;
- use a deliberate visual system rather than a generic dashboard template;
- escape data embedded in the script and cap the file/message size;
- label incomplete and unavailable periods clearly.

## Monthly refresh and delivery

- Use a no-agent updater script that regenerates the current year's JSON and HTML on the first day of each month before the morning briefing. Keep success silent and emit only a concise failure alert.
- Convert the requested local schedule to the scheduler's timezone; verify saved `next_run_at` back in the editorial timezone.
- If the daily briefing should carry the file, send it as a Telegram `sendDocument` from the briefing script only on the agreed cadence (normally the first day of the month). Read the token from the existing secret environment and chat routing from the existing non-secret config; never log either value.
- Do not trigger a real Telegram upload merely to test the integration unless the operator explicitly authorizes an immediate test. Unit-test the HTTP call with a mock and verify the next scheduled path.
- Pause or remove only the separate daily reports explicitly replaced by the consolidated briefing; keep time-sensitive alerts and unrelated newsletters unless the operator asks otherwise.

## Verification

1. Unit-test reset handling, month boundaries, missing-data status, totals/cost/ranking, HTML required elements, and document-upload request.
2. Run the official project interpreter's full relevant test suite and compile Python.
3. Run the generator/updater against live Home Assistant and inspect only aggregate output; do not print credentials or raw history.
4. Parse the generated HTML, confirm 12 month records, required chart/gauge IDs, viewport metadata, and JavaScript syntax (`node --check` when Node is available).
5. Confirm the daily and monthly cron jobs are enabled, the monthly updater precedes the daily attachment, and replaced report jobs are paused.
6. If a browser is available, render a mobile viewport and check body width, chart presence, and readable layout. If no browser can be launched, report that limitation rather than claiming visual verification.

## Pitfalls

- A device meter named `Servidor Energia total` or `Nobreak Mesa Energia total` is still individual when its label identifies a device; do not classify every string containing `total` as a household meter.
- A successful file write is not proof of a scheduled delivery; verify the saved job and a real non-sending generation path.
- Sending the HTML every day creates attachment noise; default to the first Daily of the month when the dashboard is monthly.
- Do not overwrite a production dashboard with a dry-run report unless that is intentional; use separate output paths for dry-run tests.
- Preserve historical JSON/HTML paths and use atomic replacement so a reader never sees a partial document.
