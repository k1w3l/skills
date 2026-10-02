# Chapter 12: Jobs

## Core Idea
Jobs manage batch workloads that run to successful completion — from one-shot database migrations to parallel work queues — unlike long-running services which run indefinitely.

## Frameworks Introduced
- **Job Patterns Matrix**: combine `completions` and `parallelism` to model different batch patterns.
  - One-shot (1/1): single Pod, run once.
  - Parallel fixed completions (N/M): N completions needed, M running in parallel.
  - Work queue (1/2+): drain a queue; job ends when one Pod exits zero.
- **CronJob**: schedule a Job at a cron interval.

## Reference Tables
| Pattern | completions | parallelism | Use case |
|---|---|---|---|
| One shot | 1 | 1 | DB migration, one-time task |
| Parallel fixed | 1+ | 1+ | Process N items with M workers |
| Work queue | 1 | 2+ | Drain a message queue |

## Key Concepts
- **restartPolicy**: always use `OnFailure` (retry in-place) not `Never` (creates new failed Pods per failure, fills cluster with junk).
- **completions**: total successful Pod completions required before Job is done.
- **parallelism**: max Pods running simultaneously.
- **CronJob `schedule`**: standard cron format (`"0 */5 * * *"` = every 5 hours).
- **Job cleanup**: completed Jobs and their Pods are retained for inspection; delete manually or use `ttlSecondsAfterFinished`.

## Code Examples
```yaml
# One-shot job
apiVersion: batch/v1
kind: Job
metadata:
  name: oneshot
spec:
  template:
    spec:
      containers:
      - name: kuard
        image: gcr.io/kuar-demo/kuard-amd64:blue
        command: ["/kuard", "--keygen-enable", "--keygen-exit-on-complete", "--keygen-num-to-gen=10"]
      restartPolicy: OnFailure

# Parallel job
apiVersion: batch/v1
kind: Job
spec:
  parallelism: 5
  completions: 10
  template: ...

# CronJob
apiVersion: batch/v1
kind: CronJob
spec:
  schedule: "0 */5 * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: batch-job
            image: my-batch-image
          restartPolicy: OnFailure
```

## Mental Models
- Jobs are to batch what Deployments are to services — the right controller for the job type.
- Work queue mode: set `parallelism` but omit `completions`; Job ends when first Pod exits zero.
- `kubectl run --restart=OnFailure` creates a Job; `--restart=Always` creates a Deployment/Pod.

## Anti-patterns
- **`restartPolicy: Never`**: creates a new failed Pod per failure — fills namespace with junk Pods.
- **Liveness probes without job awareness**: liveness probe kills a hung Job pod and replaces it infinitely.
- **Not labeling Jobs**: unique labels are auto-assigned; in advanced scenarios where you need to swap jobs manually, set explicit labels.

## Key Takeaways
1. Jobs are for finite workloads; use `restartPolicy: OnFailure` for retry semantics.
2. Use `parallelism` + `completions` to model parallel batch processing.
3. Work queue mode (`completions` unset, `parallelism` set) drains a queue then stops.
4. CronJobs are just scheduled Job factories — standard cron syntax.
5. Clean up completed Jobs; they retain Pods by default for log inspection.

## Connects To
- **Ch 9**: ReplicaSets for long-running services; Jobs for finite tasks.
- **Ch 13**: ConfigMaps can inject batch configuration into Job containers.
