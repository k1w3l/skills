#!/usr/bin/env python3
"""Coleta somente leitura para reconciliar o CMDB.

Não reescreve inventory/. Imprime guests, portas de LXC, containers da VM 101,
Ingress do k3s e monitores do Uptime Kuma. Sem senha, token ou connection string.

Uso: python3 ~/skills/cmdb/scripts/coletar.py
"""
import base64
import subprocess
import sys

HOST = "root@192.168.1.5"

REMOTE = r"""
import json, sqlite3, subprocess

def run(cmd):
    p = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    return p.returncode, p.stdout, p.stderr

print("== GUESTS ==")
resources = json.loads(run("pvesh get /cluster/resources --output-format json")[1])
for r in sorted((x for x in resources if x.get("type") in ("qemu","lxc")), key=lambda x: x.get("vmid",0)):
    mem = (r.get("maxmem") or 0)/1024/1024
    disk = (r.get("maxdisk") or 0)/1024/1024/1024
    print("%s\t%s\t%s\t%s\tcpu=%s\tram=%dMB\tdisk=%.1fG\ttpl=%s" % (
        r["type"], r["vmid"], r.get("name"), r.get("status"), r.get("maxcpu"), mem, disk, r.get("template")))

print("\n== LXC IP/MEM/DISK ==")
for r in sorted((x for x in resources if x.get("type")=="lxc" and not x.get("template")), key=lambda x: x.get("vmid",0)):
    rc, so, se = run("pct config %s" % r["vmid"])
    ip=mem=disk=cores="?"
    for line in so.splitlines():
        if line.startswith("net0:"):
            for part in line.split(","):
                if part.startswith("ip="):
                    ip=part.split("=",1)[1]
        elif line.startswith("memory:"):
            mem=line.split(":",1)[1].strip()
        elif line.startswith("cores:"):
            cores=line.split(":",1)[1].strip()
        elif line.startswith("rootfs:"):
            disk=line
    print("%s\t%s\tip=%s\tcores=%s\tmem=%s\t%s" % (r["vmid"], r.get("name"), ip, cores, mem, disk))

print("\n== LXC PORTS ==")
for r in sorted((x for x in resources if x.get("type")=="lxc" and x.get("status")=="running"), key=lambda x: x.get("vmid",0)):
    rc, so, se = run("pct exec %s -- ss -lntH 2>/dev/null || pct exec %s -- netstat -lnt 2>/dev/null" % (r["vmid"], r["vmid"]))
    ports=[]
    for line in so.splitlines():
        parts=line.split()
        if len(parts) < 4:
            continue
        local = parts[3] if ":" in parts[3] else (parts[3] if False else parts[-2] if ":" in parts[-2] else parts[3])
        if any(local.endswith(":"+p) or local.endswith("."+p) for p in ("22","25","53")):
            continue
        if local not in ports:
            ports.append(local)
    print("%s\t%s" % (r["vmid"], " ".join(ports) or "-"))

print("\n== DOCKER 101 ==")
rc, so, se = run("qm guest exec 101 -- bash -lc \"docker ps --format '{{.Names}}|{{.Ports}}'\"")
if rc==0:
    try:
        print(json.loads(so).get("out-data","").rstrip())
    except Exception:
        print(so[:4000])
else:
    print("FAIL", se[-300:])

print("\n== K3S INGRESS ==")
rc, so, se = run("qm guest exec 126 -- bash -lc \"sudo -n kubectl get ingress -A --no-headers\"")
if rc==0:
    try:
        print(json.loads(so).get("out-data","").rstrip())
    except Exception:
        print(so[:4000])
else:
    print("FAIL", se[-300:])

print("\n== KUMA ==")
code = r'''
import sqlite3
con = sqlite3.connect("file:/root/kuma/kuma.db?mode=ro", uri=True)
cur = con.cursor()
n = cur.execute("select count(*) from monitor").fetchone()[0]
a = cur.execute("select count(*) from monitor where active=1").fetchone()[0]
print("count", n, "active", a)
for row in cur.execute("select id,name,type,hostname,port,active from monitor order by name"):
    print("\t".join("" if v is None else str(v) for v in row))
'''
payload = __import__("base64").b64encode(code.encode()).decode()
rc, so, se = run("pct exec 110 -- python3 -c \"import base64; exec(base64.b64decode('%s').decode())\"" % payload)
print(so if rc==0 else se[-500:])
"""

def main():
    payload = base64.b64encode(REMOTE.encode()).decode()
    remote = "echo %s | base64 -d | python3" % payload
    r = subprocess.run(
        ["ssh", "-F", "/dev/null", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10",
         "-o", "StrictHostKeyChecking=accept-new", HOST, remote],
        text=True)
    return r.returncode

if __name__ == "__main__":
    sys.exit(main())
