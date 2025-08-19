#!/usr/bin/env python3
"""
OpenAPI asosida to'liq smoke-test: barcha yo'llarni avtomatik aylanadi.
- BASE_URL: default http://0.0.0.0:8004 (env: BASE_URL)
- Login: /api/v1/login/access-token (form) -> fallback: /api/v1/login (json)
- Auth header barcha so'rovlarga qo'llanadi (mavjud bo'lsa)
- GET lar: uriladi.
- POST/PUT/PATCH/DELETE: default SKIPPED, faqat xavfsiz allowlist POST lar uriladi.
- Path paramlar: list endpointdan ID olib to'ldiriladi yoki 1 bilan uriniladi.
- Hisobot: konsol + scripts/reports/openapi_full_smoke_report.{json,md}
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import requests

DEFAULT_BASE = os.environ.get("BASE_URL", "http://0.0.0.0:8004")
TIMEOUT = float(os.environ.get("SMOKE_TIMEOUT", "30"))
REPORT_DIR = os.path.join(os.path.dirname(__file__), "reports")
SESSION = requests.Session()

# POST endpointlar uchun xavfsiz allowlist (tizim holatini o'zgartirmaydi yoki test uchun xavfsiz)
SAFE_POST_ALLOWLIST = {
    "/api/v1/login/access-token",
    "/api/v1/login",
    "/api/v1/ai/analyze-answer",
}

# Ba'zi stream yoki fayl talab qiluvchi endpointlar (SKIP qilish uchun)
STREAM_OR_FILE_ENDPOINT_HINTS = [
    "/ai/tts",
    "/ai/stt",
    "/ai/voice-loop",
]


# Potentially harmful endpoints that invalidate auth or hit external services
HARMFUL_ENDPOINT_HINTS = [
    "/logout",
    "webhook",
    "create-checkout-session",
]


@dataclass
class Result:
    method: str
    path: str
    url: str
    status: str  # PASSED / FAILED / SKIPPED
    http_status: Optional[int] = None
    reason: str = ""
    duration_ms: Optional[int] = None
    error: str = ""


@dataclass
class Context:
    base_url: str
    token: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)
    openapi: Dict[str, Any] = field(default_factory=dict)
    cache_lists: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    # Payload overrides: {(METHOD, PATH): {"json": ..., "data": ..., "params": ...}}
    payloads: Dict[Tuple[str, str], Dict[str, Any]] = field(default_factory=dict)


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def login_for_token(ctx: Context) -> Optional[str]:
    user = os.environ.get("FIRST_SUPERUSER", "admin@example.com")
    pwd = os.environ.get("FIRST_SUPERUSER_PASSWORD", "changethis")

    # 1) FastAPI typical oauth2 password flow (form)
    try:
        resp = SESSION.post(
            f"{ctx.base_url}/api/v1/login/access-token",
            data={"username": user, "password": pwd},
            timeout=TIMEOUT,
        )
        if resp.ok:
            data = resp.json()
            token = data.get("access_token") or data.get("accessToken") or data.get("token")
            if token:
                return token
    except Exception as ex:
        eprint(f"login(access-token) exception: {ex}")

    # 2) Fallback: JSON body login
    try:
        resp = SESSION.post(
            f"{ctx.base_url}/api/v1/login",
            json={"username": user, "password": pwd},
            timeout=TIMEOUT,
        )
        if resp.ok:
            data = resp.json()
            token = data.get("access_token") or data.get("accessToken") or data.get("token")
            if token:
                return token
    except Exception as ex:
        eprint(f"login(/login) exception: {ex}")

    return None


def load_openapi(ctx: Context) -> Dict[str, Any]:
    # 1) Remote
    try:
        resp = SESSION.get(f"{ctx.base_url}/openapi.json", timeout=TIMEOUT)
        if resp.ok:
            return resp.json()
    except Exception as ex:
        eprint(f"openapi remote load failed: {ex}")
    # 1b) Remote (versioned path used by our FastAPI app)
    try:
        resp = SESSION.get(f"{ctx.base_url}/api/v1/openapi.json", timeout=TIMEOUT)
        if resp.ok:
            return resp.json()
    except Exception as ex:
        eprint(f"openapi remote (/api/v1/openapi.json) load failed: {ex}")

    # 2) Local file fallback
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    local_path = os.path.join(root, "openapi.json")
    if os.path.exists(local_path):
        with open(local_path, "r", encoding="utf-8") as f:
            return json.load(f)
    raise RuntimeError("OpenAPI sxema topilmadi (remote ham, lokal ham yo'q)")


def _resolve_ref(ref: str, spec: Dict[str, Any]) -> Dict[str, Any]:
    # e.g. '#/components/schemas/MySchema'
    parts = ref.lstrip('#/').split('/')
    cur: Any = spec
    for p in parts:
        cur = cur.get(p, {}) if isinstance(cur, dict) else {}
    return cur if isinstance(cur, dict) else {}


def _schema_example_or_default(schema: Dict[str, Any], spec: Dict[str, Any]) -> Any:
    if not isinstance(schema, dict):
        return None
    # Prefer explicit example/default
    if 'example' in schema:
        return schema['example']
    if 'default' in schema:
        return schema['default']
    # Resolve $ref
    if '$ref' in schema:
        return _schema_example_or_default(_resolve_ref(schema['$ref'], spec), spec)
    # Handle composition
    for key in ('oneOf', 'anyOf', 'allOf'):
        if key in schema and isinstance(schema[key], list) and schema[key]:
            return _schema_example_or_default(schema[key][0], spec)
    t = schema.get('type')
    fmt = schema.get('format')
    enum = schema.get('enum')
    if enum and isinstance(enum, list) and enum:
        return enum[0]
    if t == 'object':
        props = schema.get('properties', {}) or {}
        required = schema.get('required', []) or []
        obj = {}
        for k, v in props.items():
            if required and k not in required:
                # include minimal set: only required
                continue
            obj[k] = _schema_example_or_default(v, spec)
        # If no required specified, include a small subset
        if not obj and props:
            # include first prop
            k0, v0 = next(iter(props.items()))
            obj[k0] = _schema_example_or_default(v0, spec)
        return obj
    if t == 'array':
        items = schema.get('items', {})
        return [_schema_example_or_default(items, spec)]
    if t == 'integer':
        return 1
    if t == 'number':
        return 1.0
    if t == 'boolean':
        return True
    # string formats
    if t == 'string':
        # Add lightweight uniqueness to reduce duplicate constraint errors during tests
        ts = datetime.now().strftime('%Y%m%d%H%M%S')
        if fmt == 'email':
            return f'test_{ts}@example.com'
        if fmt == 'date-time':
            return '2025-01-01T00:00:00Z'
        if fmt == 'date':
            return '2025-01-01'
        if fmt == 'uuid':
            return '00000000-0000-0000-0000-000000000000'
        return f'string-{ts}'
    # fallback
    return 'string'


def build_request_payload(op: Dict[str, Any], spec: Dict[str, Any], override: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], Optional[str]]:
    """
    Returns (request_kwargs, skip_reason).
    request_kwargs may include json=... or data=... and headers for content-type.
    If cannot determine a safe payload (e.g., requires file), returns skip_reason.
    """
    if not isinstance(op, dict):
        return ({}, None)
    # If override provided, respect explicit fields
    if override:
        req: Dict[str, Any] = {}
        # Support params, json, data explicitly
        if isinstance(override.get('params'), dict):
            req['params'] = override['params']
        if 'json' in override:
            req['json'] = override['json']
            return (req, None)
        if 'data' in override:
            req['data'] = override['data']
            return (req, None)
        # Fallback to auto if override given but empty
    req_body = op.get('requestBody')
    if not req_body:
        return ({}, None)
    content = req_body.get('content') or {}
    # Prefer JSON
    if 'application/json' in content:
        schema = content['application/json'].get('schema') or {}
        sample = _schema_example_or_default(schema, spec)
        return ({'json': sample}, None)
    # Fallback to form
    for ct in ('application/x-www-form-urlencoded', 'multipart/form-data'):
        if ct in content:
            # We avoid real file uploads; if multipart requires files, skip
            schema = content[ct].get('schema') or {}
            sample = _schema_example_or_default(schema, spec)
            if ct == 'multipart/form-data':
                # Heuristic: if sample contains bytes/file-like, skip
                return ({}, 'Fayl/stream talab qiladi — SKIPPED')
            return ({'data': sample}, None)
    return ({}, 'Qo‘llab-quvvatlanmagan Content-Type — SKIPPED')


def is_stream_or_file_endpoint(path: str) -> bool:
    return any(h in path for h in STREAM_OR_FILE_ENDPOINT_HINTS)


def is_harmful_endpoint(path: str) -> bool:
    return any(h in path for h in HARMFUL_ENDPOINT_HINTS)


def list_endpoint_for(path: str) -> Optional[str]:
    # '/api/v1/courses/{id}' -> '/api/v1/courses/'
    if "{" in path:
        base = path.split("{")[0]
        # agar '/...' bilan tugasa ham ro'yxat bo'lishi mumkin
        if not base.endswith("/"):
            base = base.rsplit("/", 1)[0] + "/"
        return base
    return None


def fetch_first_id(ctx: Context, list_path: str) -> Optional[Tuple[str, Any]]:
    if list_path in ctx.cache_lists:
        items = ctx.cache_lists[list_path]
    else:
        url = ctx.base_url + list_path
        resp = SESSION.get(url, headers=ctx.headers, timeout=TIMEOUT)
        if not resp.ok:
            return None
        try:
            data = resp.json()
        except Exception:
            return None
        # normalize to list: support common wrappers
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict):
            for key in ("items", "results", "data", "records"):
                if isinstance(data.get(key), list) and data.get(key):
                    items = data[key]
                    break
            else:
                items = []
        else:
            items = []
        ctx.cache_lists[list_path] = items
    if not items:
        return None
    item = items[0]
    if not isinstance(item, dict):
        return None
    # Heuristika: 'id' birinchi navbatda, aks holda *id nomli maydon
    if "id" in item:
        return ("id", item["id"])
    for k in item.keys():
        if k.endswith("_id") or k == "uuid" or k == "uid":
            return (k, item[k])
    # Qolmasa None
    return None


def fill_path_params(ctx: Context, path: str) -> Tuple[str, str]:
    # returns (final_path, reason_if_skipped)
    params = re.findall(r"\{([^}]+)\}", path)
    if not params:
        return path, ""

    list_path = list_endpoint_for(path)
    id_pair = fetch_first_id(ctx, list_path) if list_path else None

    final_path = path
    for p in params:
        val: Any = 1
        if id_pair:
            # Prefer discovered id regardless of param name to avoid 404 on ".../{resource_id}"
            key, id_val = id_pair
            val = id_val
        final_path = final_path.replace("{" + p + "}", str(val))

    # Agar 1 bilan to'ldirgan bo'lsak va resurs mavjud bo'lmasa, 404 bo'lishi mumkin — bu SKIP sababi bo'ladi
    return final_path, ""


def should_skip_method(method: str, path: str, full_write: bool, allow_destructive: bool) -> Optional[str]:
    m = method.upper()
    if m == "GET":
        return None
    if m in ("PUT", "PATCH", "DELETE"):
        if not allow_destructive:
            return "Destruktiv metod (PUT/PATCH/DELETE) — default SKIPPED"
        # Allowed if explicitly requested
        if m == "DELETE" and is_stream_or_file_endpoint(path):
            return "Fayl/stream talab qiladi — SKIPPED"
        return None
    if m == "POST":
        if path in SAFE_POST_ALLOWLIST and not is_stream_or_file_endpoint(path):
            return None
        if full_write:
            # Hali ham fayl talab qilsa yoki stream bo'lsa, SKIP
            if is_stream_or_file_endpoint(path):
                return "Fayl/stream talab qiladi — SKIPPED"
            return None
        return "POST xavfsiz ro'yxatda emas — SKIPPED"
    return None


def run_endpoint(ctx: Context, method: str, path: str, op: Dict[str, Any], full_write: bool) -> Result:
    filled_path, _ = fill_path_params(ctx, path)
    url = ctx.base_url + filled_path

    try:
        req_kwargs: Dict[str, Any] = {'headers': ctx.headers, 'timeout': TIMEOUT}
        # Apply params override even for GET
        override = ctx.payloads.get((method.upper(), path)) or ctx.payloads.get((method.upper(), filled_path))
        if override and isinstance(override.get('params'), dict):
            req_kwargs['params'] = override['params']
        if full_write and method.upper() not in ('GET', 'DELETE'):
            body_kwargs, skip_reason = build_request_payload(op, ctx.openapi, override)
            if skip_reason:
                return Result(method, path, url, 'SKIPPED', reason=skip_reason)
            req_kwargs.update(body_kwargs)

        resp = SESSION.request(method.upper(), url, **req_kwargs)
        code = resp.status_code
        if 200 <= code < 300:
            return Result(method, path, url, "PASSED", http_status=code)
        # Auth talab qilishi mumkin
        if code in (401, 403):
            return Result(method, path, url, "SKIPPED", http_status=code, reason=f"Auth kerak yoki ruxsat yo'q ({code})")
        if code == 404:
            return Result(method, path, url, "SKIPPED", http_status=code, reason="Resurs topilmadi (404)")
        return Result(method, path, url, "FAILED", http_status=code, reason=f"HTTP {code}: {resp.text[:200]}")
    except Exception as ex:
        return Result(method, path, url, "FAILED", reason=str(ex))


def generate_reports(results: List[Result]) -> Tuple[str, str]:
    os.makedirs(REPORT_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    # JSON
    json_path = os.path.join(REPORT_DIR, f"openapi_full_smoke_report_{ts}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump([r.__dict__ for r in results], f, ensure_ascii=False, indent=2)

    # Markdown xulosa
    passed = sum(1 for r in results if r.status == "PASSED")
    failed = sum(1 for r in results if r.status == "FAILED")
    skipped = sum(1 for r in results if r.status == "SKIPPED")

    md_lines = [
        f"# OpenAPI Full Smoke Report ({ts})",
        "",
        f"- PASSED: {passed}",
        f"- FAILED: {failed}",
        f"- SKIPPED: {skipped}",
        "",
        "## Tafsilotlar",
    ]
    for r in results:
        md_lines.append(f"- {r.method} {r.path} -> {r.status} ({r.http_status or '-'}) {('- ' + r.reason) if r.reason else ''}")

    md_path = os.path.join(REPORT_DIR, f"openapi_full_smoke_report_{ts}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    return json_path, md_path


def parse_endpoints_file(file_path: str) -> List[Tuple[str, str]]:
    items: List[Tuple[str, str]] = []
    if not os.path.exists(file_path):
        print(f"[warn] Endpoints file yo'q: {file_path}")
        return items
    with open(file_path, 'r', encoding='utf-8') as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            method = parts[0].upper()
            path = parts[1]
            if not path.startswith('/'):
                continue
            items.append((method, path))
    return items

def main():
    parser = argparse.ArgumentParser(description="OpenAPI asosida to'liq smoke-test")
    parser.add_argument("--base", default=DEFAULT_BASE, help="BASE URL, masalan http://0.0.0.0:8004")
    parser.add_argument("--full-write", action="store_true", help="Body talab qiluvchi endpointlar uchun minimal payload yuborish")
    parser.add_argument("--allow-destructive", action="store_true", help="PUT/PATCH/DELETE metodlarini ham sinash (ogohlantirish: destruktiv)")
    parser.add_argument("--endpoints-file", default="", help="Qo'shimcha METHOD PATH ro'yxati (har qatorda: METHOD /path)")
    parser.add_argument("--payloads-file", default="", help="Per-endpoint payload overrides JSON fayli")
    parser.add_argument("--only-file", action="store_true", help="Faqat --endpoints-file dagi endpointlarni sinash, OpenAPI ro'yxatini o'tkazib yuborish")
    args = parser.parse_args()

    ctx = Context(base_url=args.base.rstrip("/"))
    # Payload overrides yuklash
    if args.payloads_file:
        try:
            with open(args.payloads_file, 'r', encoding='utf-8') as f:
                raw = json.load(f)
            payloads: Dict[Tuple[str, str], Dict[str, Any]] = {}
            if isinstance(raw, dict):
                # {'METHOD PATH': {...}} yoki {'METHOD': {'/path': {...}}}
                for k, v in raw.items():
                    if not isinstance(v, dict):
                        continue
                    if ' ' in k:
                        m, p = k.split(' ', 1)
                        payloads[(m.upper(), p.strip())] = v
                    else:
                        # nested format
                        method = k.upper()
                        for pth, pv in v.items():
                            if isinstance(pv, dict):
                                payloads[(method, pth)] = pv
            ctx.payloads = payloads
            print(f"[payloads] {len(ctx.payloads)} override yuklandi")
        except Exception as ex:
            eprint(f"[payloads] Yuklashda xatolik: {ex}")

    # Login (token ixtiyoriy, lekin ko'p endpointlar uchun kerak bo'ladi)
    token = login_for_token(ctx)
    if token:
        ctx.token = token
        ctx.headers["Authorization"] = f"Bearer {token}"
        print("[auth] Token olindi")
    else:
        print("[auth] Token olinmadi — public va 401/403 bo'lmagan endpointlar sinovdan o'tadi")

    results: List[Result] = []

    # 1) OpenAPI dagi endpointlar (faqat --only-file bo'lmaganda)
    if not args.only_file:
        # OpenAPI sxema yuklash
        ctx.openapi = load_openapi(ctx)
        paths: Dict[str, Any] = ctx.openapi.get("paths", {})

        for path, ops in sorted(paths.items(), key=lambda kv: kv[0]):
            for method, op in ops.items():
                method_upper = method.upper()
                reason = should_skip_method(method_upper, path, args.full_write, args.allow_destructive)
                if reason:
                    results.append(Result(method_upper, path, ctx.base_url + path, "SKIPPED", reason=reason))
                    continue

                # Agar requestBody talab qilsa va bizda default yo'q bo'lsa — SKIP
                req_body = op.get("requestBody") if isinstance(op, dict) else None
                if req_body and method_upper not in ("GET", "DELETE") and not args.full_write:
                    results.append(Result(method_upper, path, ctx.base_url + path, "SKIPPED", reason="Body talab qiladi — full-write yoqilmagan"))
                    continue

                # Harmful endpoints (logout, webhook, etc.)
                if is_harmful_endpoint(path):
                    results.append(Result(method_upper, path, ctx.base_url + path, "SKIPPED", reason="Harmful/external side-effect ehtimoli"))
                    continue

                # Fayl/stream endpointlarini SKIP
                if is_stream_or_file_endpoint(path):
                    results.append(Result(method_upper, path, ctx.base_url + path, "SKIPPED", reason="Fayl/stream talab qiladi"))
                    continue

                res = run_endpoint(ctx, method_upper, path, op if isinstance(op, dict) else {}, args.full_write)
                results.append(res)

    # 2) Qo'shimcha METHOD PATH ro'yxati
    if args.endpoints_file:
        extra_items = parse_endpoints_file(args.endpoints_file)
        for method_upper, path in extra_items:
            reason = should_skip_method(method_upper, path, args.full_write, args.allow_destructive)
            if reason:
                results.append(Result(method_upper, path, ctx.base_url + path, "SKIPPED", reason=reason))
                continue
            # Harmful endpoints (logout, webhook, etc.)
            if is_harmful_endpoint(path):
                results.append(Result(method_upper, path, ctx.base_url + path, "SKIPPED", reason="Harmful/external side-effect ehtimoli"))
                continue
            if is_stream_or_file_endpoint(path):
                results.append(Result(method_upper, path, ctx.base_url + path, "SKIPPED", reason="Fayl/stream talab qiladi"))
                continue
            # Qo'shimcha ro'yxatda requestBody sxemasi yo'q, shuning uchun full-write bo'lmasa ehtiyotkorlik bilan SKIP
            if method_upper not in ("GET", "DELETE") and not args.full_write:
                results.append(Result(method_upper, path, ctx.base_url + path, "SKIPPED", reason="Body talab qilishi mumkin — full-write yoqilmagan"))
                continue
            # Payload bo'lmasa — minimal {} yuboramiz (ba'zilari 422 qaytarishi tabiiy)
            filled_path, _ = fill_path_params(ctx, path)
            url = ctx.base_url + filled_path
            try:
                req_kwargs: Dict[str, Any] = {'headers': ctx.headers, 'timeout': TIMEOUT}
                # payload override
                override = ctx.payloads.get((method_upper, path)) or ctx.payloads.get((method_upper, filled_path))
                if override and isinstance(override.get('params'), dict):
                    req_kwargs['params'] = override['params']
                if method_upper not in ("GET", "DELETE") and args.full_write:
                    if override:
                        if 'json' in override:
                            req_kwargs['json'] = override['json']
                        elif 'data' in override:
                            req_kwargs['data'] = override['data']
                        else:
                            req_kwargs['json'] = {}
                    else:
                        req_kwargs['json'] = {}
                resp = SESSION.request(method_upper, url, **req_kwargs)
                code = resp.status_code
                if 200 <= code < 300:
                    results.append(Result(method_upper, path, url, "PASSED", http_status=code))
                elif code in (401, 403):
                    results.append(Result(method_upper, path, url, "SKIPPED", http_status=code, reason="Auth talab qilinadi yoki ruxsat yo'q"))
                elif code in (400, 422):
                    results.append(Result(method_upper, path, url, "SKIPPED", http_status=code, reason="Invalid payload yoki majburiy maydonlar yetishmaydi"))
                else:
                    results.append(Result(method_upper, path, url, "FAILED", http_status=code, error=resp.text[:500]))
            except Exception as e:
                results.append(Result(method_upper, path, url, "FAILED", error=str(e)))
            # Print last result summary line
            last = results[-1]
            status_icon = {"PASSED": "✅", "FAILED": "❌", "SKIPPED": "⏭"}.get(last.status, "-")
            print(f"{status_icon} {method_upper} {filled_path} -> {last.status} {last.http_status or ''} {last.reason}")

    json_path, md_path = generate_reports(results)
    print("\nHisobotlar:")
    print(f"- JSON: {json_path}")
    print(f"- MD:   {md_path}")


if __name__ == "__main__":
    main()
