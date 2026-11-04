#!/usr/bin/env python3
"""Narrow Projex transport; business decisions and recovery belong to SKILL.md."""

import argparse
import json
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import cast
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import HTTPRedirectHandler, Request, build_opener


DEFAULT_ORGANIZATION_ID = "659b8196e29648ed55c8f571"
DEFAULT_PROJECT_ID = "ab491d6f94800aaeb9ef68e915"
API_ORIGIN = "https://openapi-rdc.aliyuncs.com"
logger = logging.getLogger(__name__)


class ProjexError(Exception):
    """A request failed or its response could not be interpreted."""


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req: Request, fp: object, code: int, msg: str, headers: object, newurl: str) -> None:
        return None


@dataclass(frozen=True)
class ApiRequest:
    method: str
    path: str
    body: dict[str, object] | None = None


def identifier(value: str) -> str:
    if not value.strip() or value in {".", ".."}:
        raise ProjexError("ID must be nonempty and cannot be a relative path.")
    return quote(value, safe="")


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--organization-id", default=DEFAULT_ORGANIZATION_ID)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("project", "get", "comments", "workflow", "attachments", "file", "status", "comment"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("id")
        if command == "status":
            subparser.add_argument("--status-id", required=True)
        if command == "comment":
            subparser.add_argument("--body-file", type=Path, required=True)
        if command == "file":
            subparser.add_argument("--file-id", required=True)
    search = subparsers.add_parser("search", help="Read-only search of project bugs, one page per call")
    search.add_argument("--project-id", default=DEFAULT_PROJECT_ID)
    search.add_argument("--page", type=int, default=1)
    search.add_argument("--per-page", type=int, default=200)
    return parser


def make_request(args: argparse.Namespace) -> ApiRequest:
    prefix = f"/oapi/v1/projex/organizations/{identifier(args.organization_id)}"
    if args.command == "search":
        if args.page < 1 or not 1 <= args.per_page <= 200 or args.page * args.per_page > 10000:
            raise ProjexError("Search requires page >= 1, 1 <= per-page <= 200, and page * per-page <= 10000.")
        return ApiRequest("POST", f"{prefix}/workitems:search", {
            "category": "Bug", "spaceId": args.project_id, "spaceType": "Project",
            "page": args.page, "perPage": args.per_page, "orderBy": "gmtCreate", "sort": "desc",
        })
    if args.command == "project":
        return ApiRequest("GET", f"{prefix}/projects/{identifier(args.id)}")
    path = f"{prefix}/workitems/{identifier(args.id)}"
    if args.command in {"comments", "workflow", "attachments"}:
        return ApiRequest("GET", f"{path}/{args.command}")
    if args.command == "file":
        return ApiRequest("GET", f"{path}/files/{identifier(args.file_id)}")
    if args.command == "status":
        if not args.status_id.strip():
            raise ProjexError("Status ID must be nonempty.")
        return ApiRequest("PUT", path, {"status": args.status_id})
    if args.command == "comment":
        content = args.body_file.read_text(encoding="utf-8")
        if not content.strip():
            raise ProjexError("Comment file must be nonempty.")
        return ApiRequest("POST", f"{path}/comments", {"content": content, "formatType": "MARKDOWN"})
    return ApiRequest("GET", path)


def decode_response(raw: bytes) -> object:
    if not raw.strip():
        return None
    try:
        return cast(object, json.loads(raw))
    except (ValueError, UnicodeError) as error:
        raise ProjexError("Response is not valid JSON; verify the API endpoint and authentication.") from error


def send_request(api_request: ApiRequest, token: str) -> dict[str, object]:
    body = None if api_request.body is None else json.dumps(api_request.body, ensure_ascii=False).encode("utf-8")
    request = Request(API_ORIGIN + api_request.path, data=body, method=api_request.method, headers={
        "Accept": "application/json", "Content-Type": "application/json", "x-yunxiao-token": token,
    })
    try:
        with build_opener(NoRedirect()).open(request, timeout=30) as response:
            response_body = decode_response(response.read())
            pagination = {
                key: value for key, value in response.headers.items()
                if key.lower().startswith("x-pagination-") or key.lower() in {"x-total-count", "x-total-pages", "link"}
            }
            if isinstance(response_body, dict) and (
                response_body.get("success") is False or response_body.get("status") is False
            ):
                raise ProjexError(f"API reported failure: {json.dumps(response_body, ensure_ascii=False)}")
            return {"body": response_body, "pagination": pagination}
    except HTTPError as error:
        try:
            detail = error.read().decode("utf-8", errors="replace")
        finally:
            error.close()
        raise ProjexError(f"HTTP {error.code}: {detail}") from error
    except (URLError, TimeoutError, OSError) as error:
        message = f"Network error ({type(error).__name__}); result may be unknown. Do not retry writes blindly."
        raise ProjexError(message) from error


def main() -> int:
    args = make_parser().parse_args()
    token = os.environ.get("ALIYUN_YUNXIAO_TOKEN", "").strip()
    if not token:
        logger.error("ALIYUN_YUNXIAO_TOKEN is empty or unset; run in a login shell or configure the environment.")
        return 2
    try:
        result = send_request(make_request(args), token)
        sys.stdout.write(json.dumps(result, ensure_ascii=False, indent=2).replace(token, "[REDACTED]") + "\n")
    except (ProjexError, OSError, UnicodeError) as error:
        logger.error(str(error).replace(token, "[REDACTED]"))
        return 1
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR, format="%(message)s")
    raise SystemExit(main())
