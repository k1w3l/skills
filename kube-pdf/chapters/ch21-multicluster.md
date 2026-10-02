# Chapter 21: Multicluster Application Deployments

## Core Idea
Multicluster deployments are a necessity for resilience, latency, compliance, and isolation — but require foundational automation, consistent identity, and a global load-balancing strategy before adding the complexity.

## Frameworks Introduced
- **Get Foundations Right First**: automation, consistent identity, consistent RBAC, policy-as-code, and consistent tooling must be solid in a single cluster before multiplying across many.
- **Three Cross-Regional Architectures**:
  1. **Replicated Silos**: full copy of app per region. Simple, but inefficient (over-provisioned in small regions).
  2. **Regional Data Sharding**: split dataset across regions; add routing layer to find correct shard.
  3. **Microservice Routing**: each microservice is its own independently load-balanced global service.
- **GeoDNS vs Anycast**: two global load-balancing strategies at the DNS/network layer.

## Key Concepts
- **Single Failure Domain**: a single cluster (usually single datacenter) can fail completely.
- **GeoDNS**: route traffic based on client geography via different DNS responses. Drawback: DNS caching delays failover.
- **Anycast**: single IP advertised from multiple locations; routing protocol directs to "nearest" endpoint. Better than GeoDNS but requires cloud/network support.
- **Strong vs Eventual Consistency**: strong = write doesn't succeed until replicated (expensive, fewer TPS); eventual = write succeeds immediately, replication happens later (cheap, higher TPS, potential stale reads).
- **"Can I read my own write?"**: the key consistency question for multi-region state.
- **Replicated Silos**: simple but wasteful — every cluster sized for largest region.
- **Data Sharding**: efficient but adds cross-region routing logic.

## Mental Models
- Fix your single-cluster foundation before multiplying; problems at scale are 10x harder with 10 clusters.
- Consistency model choice is architectural — hard to change later. Choose early.
- Start with replicated silos; refactor to sharding/microservice routing as scale demands.

## Anti-patterns
- **Multicluster without automation**: manual consistency is impossible across multiple clusters.
- **Different cluster versions/tooling across regions**: variance causes "weird" bugs that don't reproduce.
- **Shared certificates/credentials across clusters**: a single compromised cluster compromises all.
- **Self-managing replicated stateful storage**: extremely complex; use cloud-managed databases unless at very large scale.

## Key Takeaways
1. Automation is the prerequisite: clusters, deployments, monitoring, RBAC — all via code.
2. Use a single identity provider (Azure AD, Google Workspace) for all clusters.
3. GeoDNS failover is slow (DNS TTL caching); anycast or HTTP-layer routing is better.
4. Choose strong vs eventual consistency before designing multicluster state.
5. Replicated silos → sharding → microservice routing: pick the simplest that fits your scale.

## Connects To
- **Ch 22**: Application organization and CI/CD for managing deployments across environments.
- **Ch 14**: Central RBAC across clusters via cloud provider integrations.
- **Ch 16**: Replicated storage strategy for multicluster data.
