# Chapter 13: ConfigMaps and Secrets

## Core Idea
ConfigMaps and Secrets decouple configuration from container images, enabling the same image to run in dev/staging/production by varying only the injected configuration.

## Frameworks Introduced
- **Three Injection Methods**: filesystem (volume mount), environment variables, command-line arguments.
  - When to use: Files for config files; env vars for simple key-value; CLI args when the app expects flags.
- **Secret vs ConfigMap Decision**: use Secret for anything sensitive (passwords, tokens, TLS keys); ConfigMap for everything else.

## Key Concepts
- **ConfigMap**: key/value store for non-sensitive config; values are UTF-8 text.
- **Secret**: key/value store for sensitive data; values are base64-encoded; stored on tmpfs (RAM disk) on nodes.
- **Secret types**: `Opaque` (generic), `kubernetes.io/tls` (TLS cert+key), `kubernetes.io/dockerconfigjson` (image pull secret).
- **imagePullSecrets**: Pod field that references a docker-registry Secret for pulling from private registries.
- **Live updates**: ConfigMaps/Secrets mounted as volumes are automatically updated in Pods (no restart needed); env vars are NOT live-updated (require Pod restart).
- **Max size**: 1 MB per ConfigMap or Secret.
- **Base64**: Secret values are base64-encoded in YAML — NOT encrypted. Encryption at rest requires cluster-level config.

## Code Examples
```bash
# Create ConfigMap
kubectl create configmap my-config \
  --from-file=my-config.txt \
  --from-literal=extra-param=extra-value

# Create Secret (generic)
kubectl create secret generic kuard-tls \
  --from-file=kuard.crt --from-file=kuard.key

# Create image pull secret
kubectl create secret docker-registry my-pull-secret \
  --docker-username=<user> --docker-password=<pass> --docker-email=<email>

# View raw values
kubectl get secret kuard-tls -o yaml
kubectl get configmap my-config -o yaml

# Live update from file
kubectl create secret generic kuard-tls \
  --from-file=kuard.crt --from-file=kuard.key \
  --dry-run=client -o yaml | kubectl replace -f -
```

```yaml
# Pod using ConfigMap all three ways
spec:
  containers:
  - name: app
    image: myapp
    command: ["/app", "$(EXTRA_PARAM)"]      # CLI arg from env var
    env:
    - name: ANOTHER_PARAM
      valueFrom:
        configMapKeyRef:
          name: my-config
          key: another-param
    volumeMounts:
    - name: config-volume
      mountPath: /config
  volumes:
  - name: config-volume
    configMap:
      name: my-config
```

## Mental Models
- ConfigMap = application configuration as a first-class Kubernetes object.
- Volume-mounted configs auto-update; env vars don't — plan accordingly.
- Base64 in a Secret YAML is obfuscation, not encryption. Store Secret YAMLs in a secrets manager, not git.

## Anti-patterns
- **Checking Secret YAML into source control**: base64 is trivially decodable; use sealed-secrets, Vault, or cloud KMS integration.
- **Passwords baked into container images**: violates immutability and security; use Secrets.
- **Treating ConfigMap as a general database**: max 1MB; for large data, use a proper storage backend.

## Key Takeaways
1. Volume-mounted ConfigMaps/Secrets auto-update without Pod restart; env vars don't.
2. Never commit Secret YAML to source control; use Sealed Secrets, Vault, or cloud KMS.
3. `imagePullSecrets` on the default ServiceAccount propagates pull credentials to all Pods in a namespace.
4. `--dry-run=client -o yaml | kubectl replace -f -` pattern enables updating Secrets from files.
5. Kubernetes Secrets are NOT encrypted at rest by default — enable encryption with a cloud KMS integration.

## Connects To
- **Ch 2**: Container images should never bundle secrets.
- **Ch 5**: Secrets/ConfigMaps mounted in Pod spec via volumes or env vars.
- **Ch 19**: Security hardening — encryption at rest for Secrets.
