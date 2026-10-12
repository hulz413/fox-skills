# Example input/output contract

## Example URLs

- `https://leetcode.cn/problems/3sum/description/`
- `https://leetcode.cn/problems/merge-intervals/description/`

## Example metadata for one problem

- Frontend ID: `15`
- Slug: `3sum`
- Title: `3Sum`
- Card language: Chinese
- Solution language: Python 3
- Per-problem YAML filename: `leetcode_15_3sum.yaml`

## Example YAML structure for one problem

```yaml
- type: LeetCode Basic
  frontend_id: "15"
  code_language: python
  tags: [leetcode, array, two-pointers, sorting]
  fields:
    Front: |
      <div style="text-align: left;">
      <strong>3Sum</strong><br><br>
      Put the problem statement, examples, and constraints here.
      </div>
    Back: |
      <div style="text-align: left;">
      <strong>Approach Summary</strong>
      <ul>
        <li>Put the main approach points here.</li>
      </ul>
      <strong>Complexity</strong>
      <ul>
        <li>Time complexity: O(n^2)</li>
        <li>Extra space complexity: O(1)</li>
      </ul>
      <strong>Best Solution (Python 3)</strong>
      <pre><code>class Solution:
          def threeSum(self, nums):
              ...</code></pre>
      </div>
```

## Notes

- Keep one YAML source file per problem.
- One invocation may generate multiple such per-problem YAML files.
- The orchestrator manages per-problem YAML reuse/regeneration and creates one temporary hidden batch YAML for the current invocation only when a rebuild is needed.
- Keep code blocks as plain `<pre><code>...</code></pre>`.
- Do not hand-write highlighted HTML.
- The hidden builder will add syntax highlighting during package generation.
- The `code_language` field controls syntax highlighting.
- If `code_language` is missing, the builder must default to Python 3.
- The same problem must always use the same per-problem YAML file.
- New YAML should include `frontend_id`; legacy YAML that still carries `leetcode-<id>` remains builder-compatible.
- If that YAML file already exists and the user did not ask to refresh it, it may be reused as-is.
