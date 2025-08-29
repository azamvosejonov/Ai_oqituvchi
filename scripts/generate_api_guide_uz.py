#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenAPI -> API_GUIDE_UZ.v2.md generator

- Reads openapi.json from project root
- Produces a Uzbek API guide with a uniform format per endpoint
- Focuses on: METHOD + PATH first, then JSON/Form examples, required fields, and description

Usage:
  .venv/bin/python scripts/generate_api_guide_uz.py
"""
from __future__ import annotations
import json
import os
import re
from typing import Any, Dict, List, Tuple, Optional

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OPENAPI_PATH = os.path.join(ROOT, 'openapi.json')
OUT_PATH = os.path.join(ROOT, 'API_GUIDE_UZ.v2.md')
BASE_URL = 'http://0.0.0.0:8004'
API_PREFIX = '/api/v1'

HTTP_METHODS = ['get', 'post', 'put', 'patch', 'delete']
MAX_DEPTH = 20


def load_openapi() -> Dict[str, Any]:
    with open(OPENAPI_PATH, 'r', encoding='utf-8') as f:
        data = f.read()
        # Some files may be one-line minified JSON
        return json.loads(data)


def ref_name(ref: str) -> str:
    # Example: #/components/schemas/User -> User
    return ref.split('/')[-1]


def guess_object_from_path(path: str) -> str:
    # Take last non-parameter segment
    parts = [p for p in path.strip('/').split('/') if p and not p.startswith('{')]
    if not parts:
        return ''
    noun = parts[-1]
    # Map common nouns to Uzbek
    noun_map = {
        'courses': 'kurslar', 'course': 'kurs',
        'interactive-lessons': 'interaktiv darslar', 'interactive-lesson': 'interaktiv dars',
        'subscription-plans': 'obuna rejalar', 'subscription-plan': 'obuna rejasi',
        'subscriptions': 'obunalar', 'subscription': 'obuna',
        'users': 'foydalanuvchilar', 'user': 'foydalanuvchi',
        'topics': 'mavzular', 'topic': 'mavzu',
        'posts': 'postlar', 'post': 'post',
        'comments': 'izohlar', 'comment': 'izoh',
        'payments': 'to‘lovlar', 'payment': 'to‘lov',
        'feedback': 'fikr-mulohazalar',
        'homework': 'uy vazifalari', 'files': 'fayllar', 'file': 'fayl',
        'certificates': 'sertifikatlar', 'certificate': 'sertifikat',
        'tests': 'testlar', 'test': 'test',
        'sessions': 'sessiyalar', 'session': 'sessiya',
        'statistics': 'statistika',
        'ai': 'AI', 'tts': 'matndan nutqqa', 'stt': 'nutqdan matnga',
        'forum': 'forum', 'profile': 'profil', 'roles': 'rollar', 'plans': 'rejalar'
    }
    return noun_map.get(noun, noun.replace('-', ' '))


def translate_desc_to_uz(desc: str, path: str, method: str) -> str:
    if not desc:
        desc = ''
    d = desc.strip()
    obj = guess_object_from_path(path)
    low = d.lower()

    # Common clause translations
    replaces = [
        (r'only for admins\.?', 'Faqat adminlar uchun.'),
        (r'superusers only\.?', 'Faqat superuserlar uchun.'),
        (r'requires authentication\.?', 'Autentifikatsiya talab qilinadi.'),
        (r'for the current user', 'joriy foydalanuvchi uchun'),
    ]

    # Helpers for Uzbek morphology
    def singularize(noun: str) -> str:
        parts = noun.split()
        if not parts:
            return noun
        last = parts[-1]
        if last.endswith('lar'):
            last = last[:-3]
        elif last.endswith('lar'):
            last = last[:-3]
        parts[-1] = last
        return ' '.join(parts)

    def accusative(noun: str) -> str:
        # Attach -ni directly (e.g., kurs -> kursni, kurslar -> kurslarni)
        return noun + 'ni'

    # Pattern-based main action
    patterns = [
        (r'^retrieve all (.+)\.?$', lambda m: f"Barcha {accusative(obj or m.group(1))} olish."),
        (r'^list all (.+)\.?$', lambda m: f"Barcha {accusative(obj or m.group(1))} ro‘yxatini olish."),
        (r'^create (a )?new (.+)\.?$', lambda m: f"Yangi {singularize(obj or m.group(2))} yaratish."),
        (r'^update (a |the )?(.+)\.?$', lambda m: f"{accusative(singularize(obj or m.group(2)))} yangilash."),
        (r'^delete (a |the )?(.+)\.?$', lambda m: f"{accusative(singularize(obj or m.group(2)))} o‘chirish."),
        (r'^get (a |the )?specific (.+) by id\.?$', lambda m: f"{accusative(singularize(obj or m.group(2)))} ID bo‘yicha olish."),
        (r'^get (.+) by id\.?$', lambda m: f"{accusative(singularize(obj or m.group(1)))} ID bo‘yicha olish."),
        (r'^retrieve (.+)$', lambda m: f"{accusative(obj or m.group(1))} olish."),
    ]

    for pat, fn in patterns:
        mm = re.match(pat, low)
        if mm:
            uz = fn(mm)
            # Append any clauses
            tail = low[mm.end():].strip()
            for rg, rep in replaces:
                tail = re.sub(rg, rep, tail, flags=re.IGNORECASE)
            return (uz + (' ' + tail if tail else '')).strip().rstrip('.') + '.'

    # If could not pattern-match, do clause-level replacements only
    uz = d
    for rg, rep in replaces:
        uz = re.sub(rg, rep, uz, flags=re.IGNORECASE)
    # Simple verb replacements
    verb_map = [
        (r'\bretrieve\b', 'olish'),
        (r'\bcreate\b', 'yaratish'),
        (r'\bupdate\b', 'yangilash'),
        (r'\bdelete\b', 'o‘chirish'),
        (r'\bget\b', 'olish'),
    ]
    for rg, rep in verb_map:
        uz = re.sub(rg, rep, uz, flags=re.IGNORECASE)
    return uz


def resolve_schema(schema: Dict[str, Any], components: Dict[str, Any], depth: int = 0, seen: Optional[set] = None) -> Dict[str, Any]:
    if not isinstance(schema, dict):
        return {}
    if seen is None:
        seen = set()
    if depth > MAX_DEPTH:
        return {}
    if '$ref' in schema:
        name = ref_name(schema['$ref'])
        if name in seen:
            # Break cyclic refs
            return {'type': 'object'}
        seen.add(name)
        return resolve_schema(components.get('schemas', {}).get(name, {}), components, depth+1, seen)
    # Handle oneOf/anyOf/allOf simplistically: pick first
    for key in ('oneOf', 'anyOf', 'allOf'):
        if key in schema and isinstance(schema[key], list) and schema[key]:
            return resolve_schema(schema[key][0], components, depth+1, seen)
    return schema


def example_for_schema(schema: Dict[str, Any], components: Dict[str, Any], depth: int = 0, seen: Optional[set] = None) -> Any:
    if seen is None:
        seen = set()
    if depth > MAX_DEPTH:
        return {}
    schema = resolve_schema(schema, components, depth, set(seen))
    # Prefer explicit example/default if present
    if 'example' in schema:
        return schema['example']
    if 'default' in schema:
        return schema['default']
    t = schema.get('type')
    if 'enum' in schema and isinstance(schema['enum'], list) and schema['enum']:
        return schema['enum'][0]
    if t == 'object' or ('properties' in schema):
        props = schema.get('properties', {})
        example: Dict[str, Any] = {}
        for k, v in props.items():
            example[k] = example_for_schema(v, components, depth+1, set(seen))
        # Handle additionalProperties (dict with arbitrary keys)
        addl = schema.get('additionalProperties')
        if isinstance(addl, dict):
            example['<key>'] = example_for_schema(addl, components, depth+1, set(seen))
        return example
    if t == 'array':
        items = schema.get('items', {})
        return [example_for_schema(items, components, depth+1, set(seen))]
    if t == 'integer' or t == 'number':
        return 0
    if t == 'boolean':
        return True
    if t == 'string' or t is None:
        fmt = schema.get('format')
        if fmt == 'binary':
            return '(binary file)'
        if fmt == 'date-time':
            return '2025-01-01T00:00:00Z'
        if fmt == 'date':
            return '2025-01-01'
        return 'string'
    # Fallback
    return {}


def collect_required(schema: Dict[str, Any], components: Dict[str, Any]) -> List[str]:
    s = resolve_schema(schema, components)
    req = s.get('required', [])
    if isinstance(req, list):
        return req
    return []


def is_audio_stream_response(responses: Dict[str, Any]) -> bool:
    for code, meta in responses.items():
        if not isinstance(meta, dict):
            continue
        content = meta.get('content', {})
        if 'audio/mpeg' in content or 'audio/*' in content:
            return True
    return False


def best_response_schema(responses: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    # Prefer 200, 201, 204
    for code in ('200', '201'):
        meta = responses.get(code)
        if not isinstance(meta, dict):
            continue
        content = meta.get('content', {})
        # Prefer JSON
        for ct in ('application/json', 'application/*+json', 'text/json'):
            if ct in content:
                return content[ct].get('schema')
    return None


def method_auth_hint(desc: str) -> str:
    d = (desc or '').lower()
    if 'superuser' in d or 'admin only' in d or '(admin only)' in d or 'superusers only' in d:
        return 'Ha (Admin/Superuser)'
    if 'current user' in d or 'authenticated' in d or 'requires' in d and 'token' in d:
        return 'Ha (JWT)'
    if 'only the owner' in d:
        return 'Ha (JWT, egalik tekshiruvi)'
    return 'Yo‘q (agar ko‘rsatilmagan bo‘lsa)'


def content_request_info(req_body: Dict[str, Any], components: Dict[str, Any]) -> Tuple[str, Any, List[str]]:
    # Returns (type_label, example, required_fields)
    if not req_body:
        return ('Yo‘q', None, [])
    content = req_body.get('content', {})
    # Prefer JSON
    for ct in ('application/json', 'application/*+json', 'text/json'):
        if ct in content:
            sch = content[ct].get('schema', {})
            ex = example_for_schema(sch, components)
            req = collect_required(sch, components)
            return ('JSON', ex, req)
    # Multipart form
    for ct in ('multipart/form-data', 'application/x-www-form-urlencoded'):
        if ct in content:
            sch = content[ct].get('schema', {})
            resolved = resolve_schema(sch, components)
            props = resolved.get('properties', {})
            form_example: Dict[str, Any] = {}
            for k, v in props.items():
                form_example[k] = example_for_schema(v, components)
            req = resolved.get('required', []) or []
            label = 'Form-Data' if ct == 'multipart/form-data' else 'Form-UrlEncoded'
            return (label, form_example, req)
    return ('Noma’lum', None, [])


def parameters_info(path_params: List[Dict[str, Any]], components: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], List[str]]:
    # Normalize params list (query, path, header)
    params = []
    required_names: List[str] = []
    for p in path_params or []:
        name = p.get('name')
        loc = p.get('in')
        required = bool(p.get('required'))
        schema = p.get('schema', {})
        t = resolve_schema(schema, components).get('type', 'string')
        params.append({'name': name, 'in': loc, 'required': required, 'type': t})
        if required and name:
            required_names.append(name)
    return params, required_names


def to_md_code(lang: str, obj: Any) -> str:
    if obj is None:
        return ''
    if isinstance(obj, (dict, list)):
        content = json.dumps(obj, ensure_ascii=False, indent=2)
        return f"```{lang}\n{content}\n```\n"
    return f"```{lang}\n{obj}\n```\n"


def build_endpoint_section(path: str, method: str, op: Dict[str, Any], components: Dict[str, Any]) -> str:
    title = f"{method.upper()} {path}"
    desc = op.get('description') or op.get('summary') or ''
    desc = translate_desc_to_uz(desc, path, method)

    # Parameters (path-level + method-level already merged by caller)
    params = op.get('parameters', [])
    params_info, req_param_required = parameters_info(params, components)

    # Request body
    req_body = op.get('requestBody', {}) or {}
    req_type, req_example, req_required = content_request_info(req_body, components)

    # Responses
    responses = op.get('responses', {}) or {}
    audio_stream = is_audio_stream_response(responses)
    resp_schema = best_response_schema(responses)
    resp_example = None
    if resp_schema:
        resp_example = example_for_schema(resp_schema, components)
    auth = method_auth_hint(desc)

    # Required fields combined
    combined_required = list(dict.fromkeys(req_param_required + req_required))

    lines: List[str] = []
    lines.append(f"- __[Endpoint]__ {title}")
    lines.append(f"- __[Tavsif]__ {desc.strip()}")
    lines.append(f"- __[Auth]__ {auth}")

    # Parameters table-like bullets
    if params_info:
        lines.append(f"- __[Parametrlar]__")
        for p in params_info:
            req_mark = 'Majburiy' if p['required'] else 'Ixtiyoriy'
            lines.append(f"  - {p['in']}: `{p['name']}` ({p['type']}) — {req_mark}")
    else:
        lines.append(f"- __[Parametrlar]__ Yo‘q")

    # Request
    lines.append(f"- __[So‘rov turi]__ {req_type}")
    if req_example is not None:
        lang = 'json' if req_type in ('JSON', 'Form-UrlEncoded') else 'bash'
        lines.append(to_md_code('json' if req_type == 'JSON' else 'json', req_example))

    if combined_required:
        lines.append(f"- __[Majburiy maydonlar]__ `" + '`, `'.join(combined_required) + '`')
    else:
        lines.append(f"- __[Majburiy maydonlar]__ Yo‘q")

    # Response
    if audio_stream:
        lines.append(f"- __[Javob]__ audio/mpeg (oqim)")
    elif resp_example is not None:
        lines.append(f"- __[Javob namunasi]__")
        lines.append(to_md_code('json', resp_example))
    else:
        lines.append(f"- __[Javob]__ Ko‘rsatilmagan")

    # Example cURL
    curl_lines: List[str] = []
    url = f"{BASE_URL}{path}"
    auth_header = '-H "Authorization: Bearer <TOKEN>" '
    if method.lower() == 'get':
        curl_lines.append(f"curl {auth_header if auth.startswith('Ha') else ''}\"{url}\"")
    else:
        if req_type == 'JSON' and isinstance(req_example, (dict, list)):
            body = json.dumps(req_example, ensure_ascii=False)
            curl_lines.append(
                f"curl -X {method.upper()} \"{url}\" \\\n -H 'Content-Type: application/json' {auth_header if auth.startswith('Ha') else ''}-d '{body}'"
            )
        elif req_type in ('Form-Data', 'Form-UrlEncoded') and isinstance(req_example, dict):
            # Simplified: use -F for form-data, -d for urlencoded
            if req_type == 'Form-Data':
                parts = ' \\\n' + '\n'.join([f" -F \"{k}={v}\"" for k, v in req_example.items()])
                curl_lines.append(f"curl -X {method.upper()} \"{url}\" {auth_header if auth.startswith('Ha') else ''}" + parts)
            else:
                # urlencoded
                parts = '&'.join([f"{k}={v}" for k, v in req_example.items()])
                curl_lines.append(
                    f"curl -X {method.upper()} \"{url}\" {auth_header if auth.startswith('Ha') else ''}-H 'Content-Type: application/x-www-form-urlencoded' -d '{parts}'"
                )
        else:
            curl_lines.append(f"curl -X {method.upper()} {auth_header if auth.startswith('Ha') else ''}\"{url}\"")

    lines.append(f"- __[cURL namunasi]__")
    lines.append('```bash\n' + (curl_lines[0] if curl_lines else '') + '\n```\n')

    lines.append('\n')
    return '\n'.join(lines)


def merge_path_and_method_params(path_item: Dict[str, Any], method_op: Dict[str, Any]) -> None:
    # Ensure method_op.parameters includes path-level parameters
    path_params = path_item.get('parameters', []) or []
    method_params = method_op.get('parameters', []) or []
    names = {(p.get('name'), p.get('in')) for p in method_params}
    for p in path_params:
        key = (p.get('name'), p.get('in'))
        if key not in names:
            method_params.append(p)
    if method_params:
        method_op['parameters'] = method_params


def main() -> None:
    openapi = load_openapi()
    components = openapi.get('components', {})
    info = openapi.get('info', {})
    paths = openapi.get('paths', {})

    out: List[str] = []
    out.append('# O‘quv Platformasi API Qo‘llanma — V2 (UZ)')
    out.append('')
    out.append(f"- Base URL: {BASE_URL}{API_PREFIX}")
    out.append('- Har bir endpoint bir xil formatda ko‘rsatilgan: Endpoint → Parametrlar → So‘rov → Majburiy maydonlar → Javob → cURL')
    out.append('- Auth soddalashtirilgan ko‘rinishda berilgan (Admin/Superuser yoki JWT yoki Public)')
    out.append('')

    # Group by tag to make document navigable
    tag_groups: Dict[str, List[Tuple[str, str, Dict[str, Any], Dict[str, Any]]]] = {}
    for path, path_item in paths.items():
        for method in HTTP_METHODS:
            if method in path_item:
                op = path_item[method]
                merge_path_and_method_params(path_item, op)
                tags = op.get('tags', ['misc'])
                for tag in tags:
                    tag_groups.setdefault(tag, []).append((path, method, op, components))

    # Stable ordering: tags alphabetically, then path/method
    for tag in sorted(tag_groups.keys()):
        out.append(f"## {tag}")
        for path, method, op, comps in sorted(tag_groups[tag], key=lambda x: (x[0], x[1])):
            out.append(build_endpoint_section(path, method, op, comps))

    # Write output
    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out))

    print(f"Generated: {OUT_PATH}")


if __name__ == '__main__':
    main()
