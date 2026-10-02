#!/usr/bin/env python3
"""Small Bichon API helper for Hermes skills.

Reads /home/kiwel/.hermes/secrets/bichon.env by default and never prints the API key.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

DEFAULT_ENV = Path('/home/kiwel/.hermes/secrets/bichon.env')


def load_env(path: Path = DEFAULT_ENV) -> dict[str, str]:
    vals: dict[str, str] = {}
    if not path.exists():
        raise SystemExit(f'Missing Bichon env file: {path}')
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        vals[key.strip()] = value.strip().strip('"').strip("'")
    if not vals.get('BICHON_URL') or not vals.get('BICHON_API_KEY'):
        raise SystemExit(f'{path} must define BICHON_URL and BICHON_API_KEY')
    return vals


class BichonClient:
    def __init__(self, base_url: str | None = None, api_key: str | None = None) -> None:
        if base_url is None or api_key is None:
            vals = load_env()
            base_url = base_url or vals['BICHON_URL']
            api_key=*** or vals['BICHON_API_KEY']
        self.base_url = base_url.rstrip('/')
        self.api_key=***

    def request(self, method: str, path: str, body: Any = None, *, binary: bool = False) -> Any:
        url = self.base_url + path
        data = None
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Accept': 'application/json',
            'User-Agent': 'Hermes-Bichon-Skill',
        }
        if body is not None:
            data = json.dumps(body).encode('utf-8')
            headers['Content-Type'] = 'application/json'
        req = urllib.request.Request(url, data=data, headers=headers, method=method.upper())
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                payload = resp.read()
                if binary:
                    return payload
                ctype = resp.headers.get('content-type', '')
                text = payload.decode('utf-8', 'replace')
                return json.loads(text) if 'json' in ctype or text[:1] in '[{' else text
        except urllib.error.HTTPError as exc:
            msg = exc.read().decode('utf-8', 'replace')[:2000]
            raise SystemExit(f'Bichon HTTP {exc.code} {exc.reason}: {msg}')

    def current_user(self) -> Any:
        return self.request('GET', '/api/v1/current-user')

    def accounts(self) -> Any:
        return self.request('GET', '/api/v1/minimal-account-list')

    def mailboxes(self, account_id: int, remote: bool = False) -> Any:
        return self.request('GET', f'/api/v1/list-mailboxes/{account_id}?remote={str(remote).lower()}')

    def list_messages(self, account_id: int, mailbox_id: int, page: int = 1, page_size: int = 30) -> Any:
        qs = urllib.parse.urlencode({'mailbox_id': mailbox_id, 'page': page, 'page_size': page_size})
        return self.request('GET', f'/api/v1/list-messages/{account_id}?{qs}')

    def search(self, filt: dict[str, Any], page: int = 1, page_size: int = 30, sort_by: str = 'DATE', desc: bool = True) -> Any:
        return self.request('POST', '/api/v1/search-messages', {
            'filter': filt,
            'page': page,
            'page_size': page_size,
            'sort_by': sort_by,
            'desc': desc,
        })

    def content(self, account_id: int, message_id: int) -> Any:
        return self.request('GET', f'/api/v1/message-content/{account_id}/{message_id}')

    def tag(self, account_id: int, message_ids: list[int], tags: list[str]) -> Any:
        return self.request('POST', '/api/v1/update-tags', {
            'updates': {str(account_id): message_ids},
            'tags': tags,
        })


def print_json(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Bichon API helper')
    sub = parser.add_subparsers(dest='cmd', required=True)

    sub.add_parser('whoami')
    sub.add_parser('accounts')

    p = sub.add_parser('mailboxes')
    p.add_argument('account_id', type=int)
    p.add_argument('--remote', action='store_true')

    p = sub.add_parser('messages')
    p.add_argument('account_id', type=int)
    p.add_argument('mailbox_id', type=int)
    p.add_argument('--page', type=int, default=1)
    p.add_argument('--page-size', type=int, default=30)

    p = sub.add_parser('search')
    p.add_argument('--text')
    p.add_argument('--from-email', dest='from_')
    p.add_argument('--to')
    p.add_argument('--account-id', type=int)
    p.add_argument('--mailbox-id', type=int)
    p.add_argument('--tag', action='append', dest='tags')
    p.add_argument('--has-attachment', action='store_true')
    p.add_argument('--page', type=int, default=1)
    p.add_argument('--page-size', type=int, default=30)

    p = sub.add_parser('content')
    p.add_argument('account_id', type=int)
    p.add_argument('message_id', type=int)

    p = sub.add_parser('tag')
    p.add_argument('account_id', type=int)
    p.add_argument('tags_csv', help='Comma-separated tags, e.g. compras,e-commerce')
    p.add_argument('message_ids', nargs='+', type=int)

    args = parser.parse_args(argv)
    c = BichonClient()

    if args.cmd == 'whoami':
        print_json(c.current_user())
    elif args.cmd == 'accounts':
        print_json(c.accounts())
    elif args.cmd == 'mailboxes':
        print_json(c.mailboxes(args.account_id, args.remote))
    elif args.cmd == 'messages':
        print_json(c.list_messages(args.account_id, args.mailbox_id, args.page, args.page_size))
    elif args.cmd == 'search':
        filt: dict[str, Any] = {}
        if args.text:
            filt['text'] = args.text
        if args.from_:
            filt['from'] = args.from_
        if args.to:
            filt['to'] = args.to
        if args.account_id:
            filt['account_id'] = args.account_id
        if args.mailbox_id:
            filt['mailbox_id'] = args.mailbox_id
        if args.tags:
            filt['tags'] = args.tags
        if args.has_attachment:
            filt['has_attachment'] = True
        print_json(c.search(filt, args.page, args.page_size))
    elif args.cmd == 'content':
        print_json(c.content(args.account_id, args.message_id))
    elif args.cmd == 'tag':
        tags = [t.strip().lower() for t in args.tags_csv.split(',') if t.strip()]
        print_json(c.tag(args.account_id, args.message_ids, tags))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
