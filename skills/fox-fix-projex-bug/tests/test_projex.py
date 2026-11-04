"""Offline contract checks; no live bug, credentials, Git mutations, or API calls."""

import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError, URLError

from scripts import projex


def api_response(body: object, headers: dict[str, str] | None = None) -> MagicMock:
    response = MagicMock()
    response.__enter__.return_value = response
    response.read.return_value = b"" if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
    response.headers = headers or {}
    return response


class ProjexContractTests(unittest.TestCase):
    def test_search_is_project_scoped_bug_query_with_a_bounded_page(self) -> None:
        args = projex.make_parser().parse_args(["search", "--project-id", "project-1", "--page", "2"])
        request = projex.make_request(args)
        self.assertEqual(request.method, "POST")
        self.assertTrue(request.path.endswith("/workitems:search"))
        self.assertEqual(request.body, {
            "category": "Bug", "spaceId": "project-1", "spaceType": "Project",
            "page": 2, "perPage": 200, "orderBy": "gmtCreate", "sort": "desc",
        })
        for options in (["--page", "51"], ["--page", "0"], ["--per-page", "201"]):
            with self.subTest(options=options), self.assertRaises(projex.ProjexError):
                projex.make_request(projex.make_parser().parse_args(["search", *options]))

    def test_status_write_only_changes_status_and_accepts_an_empty_success_body(self) -> None:
        args = projex.make_parser().parse_args(["status", "bug-1", "--status-id", "selected-1"])
        opener = MagicMock()
        opener.open.return_value = api_response(None)
        with patch.object(projex, "build_opener", return_value=opener):
            result = projex.send_request(projex.make_request(args), "test-token")
        request = opener.open.call_args.args[0]
        self.assertEqual(request.method, "PUT")
        self.assertTrue(request.full_url.endswith("/workitems/bug-1"))
        self.assertEqual(json.loads(request.data), {"status": "selected-1"})
        self.assertIsNone(result["body"])
        opener.open.assert_called_once()

    def test_comment_preserves_unicode_and_newlines_as_markdown(self) -> None:
        content = "原因：分页丢失\n\n修复内容：读取后续页\n\n验证结果：通过\n\nCommit：" + "a" * 40
        with tempfile.TemporaryDirectory() as directory:
            body_file = Path(directory) / "comment.md"
            body_file.write_text(content, encoding="utf-8")
            args = projex.make_parser().parse_args(["comment", "bug-1", "--body-file", str(body_file)])
            opener = MagicMock()
            opener.open.return_value = api_response({"id": "comment-1"})
            with patch.object(projex, "build_opener", return_value=opener):
                projex.send_request(projex.make_request(args), "test-token")
            request = opener.open.call_args.args[0]
            self.assertEqual(request.method, "POST")
            self.assertTrue(request.full_url.endswith("/workitems/bug-1/comments"))
            self.assertEqual(json.loads(request.data), {"content": content, "formatType": "MARKDOWN"})
            opener.open.assert_called_once()
            body_file.write_text(" \n", encoding="utf-8")
            with self.assertRaises(projex.ProjexError):
                projex.make_request(args)

    def test_read_preserves_all_items_and_pagination_metadata(self) -> None:
        comments = [{"id": str(index), "content": "评论"} for index in range(250)]
        opener = MagicMock()
        opener.open.return_value = api_response(comments, {
            "X-Pagination-Total-Count": "250", "Link": '<https://example.invalid/?page=2>; rel="next"',
        })
        with patch.object(projex, "build_opener", return_value=opener):
            result = projex.send_request(projex.ApiRequest("GET", "/comments"), "test-token")
        self.assertEqual(result["body"], comments)
        self.assertEqual(result["pagination"], opener.open.return_value.headers)

    def test_network_failure_does_not_retry_a_write(self) -> None:
        opener = MagicMock()
        opener.open.side_effect = URLError("disconnected")
        with patch.object(projex, "build_opener", return_value=opener):
            with self.assertRaisesRegex(projex.ProjexError, "result may be unknown"):
                projex.send_request(projex.ApiRequest("POST", "/comments", {"content": "修复"}), "test-token")
        opener.open.assert_called_once()

    def test_cli_redacts_a_credential_echoed_by_an_http_error(self) -> None:
        opener = MagicMock()
        opener.open.side_effect = HTTPError(
            "https://openapi-rdc.aliyuncs.com", 403, "Forbidden", {}, io.BytesIO(b"invalid test-token"),
        )
        with (
            patch.dict(projex.os.environ, {"ALIYUN_YUNXIAO_TOKEN": "test-token"}, clear=True),
            patch.object(projex.sys, "argv", ["projex.py", "get", "bug-1"]),
            patch.object(projex, "build_opener", return_value=opener),
            self.assertLogs(projex.logger, level="ERROR") as logs,
        ):
            self.assertEqual(projex.main(), 1)
        output = "\n".join(logs.output)
        self.assertIn("HTTP 403", output)
        self.assertIn("[REDACTED]", output)
        self.assertNotIn("test-token", output)
        opener.open.assert_called_once()

    def test_missing_credential_stops_before_network_access(self) -> None:
        with (
            patch.dict(projex.os.environ, {}, clear=True),
            patch.object(projex.sys, "argv", ["projex.py", "get", "bug-1"]),
            patch.object(projex, "build_opener") as opener,
            self.assertLogs(projex.logger, level="ERROR"),
        ):
            self.assertEqual(projex.main(), 2)
        opener.assert_not_called()

    def test_application_failure_and_invalid_json_do_not_report_success(self) -> None:
        for body in ({"success": False, "message": "denied"}, {"status": False}):
            opener = MagicMock()
            opener.open.return_value = api_response(body)
            with patch.object(projex, "build_opener", return_value=opener):
                with self.assertRaisesRegex(projex.ProjexError, "API reported failure"):
                    projex.send_request(projex.ApiRequest("GET", "/bug"), "test-token")
        with self.assertRaisesRegex(projex.ProjexError, "not valid JSON"):
            projex.decode_response(b"<html>login</html>")

    def test_no_redirect_and_ids_cannot_change_the_request_origin(self) -> None:
        self.assertIsNone(projex.NoRedirect().redirect_request(None, None, 302, "redirect", None, "https://invalid"))
        args = projex.make_parser().parse_args(["get", "https://other.invalid/bug?x=1#frag"])
        request = projex.make_request(args)
        self.assertIn("https%3A%2F%2Fother.invalid%2Fbug%3Fx%3D1%23frag", request.path)
        self.assertEqual((projex.API_ORIGIN + request.path).split("/", 3)[2], "openapi-rdc.aliyuncs.com")


if __name__ == "__main__":
    unittest.main()
