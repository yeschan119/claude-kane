# claude-kiss

Claude Code 를 위한 **최소 개발 하네스** 플러그인입니다. 설치하면 어느 레포에서든 같은 개발 규칙과 안전장치가 바로 적용됩니다.
기능이 많은 오케스트레이션 플러그인과 달리, 실제로 매일 쓰는 것만 남겼습니다 — **KISS · YAGNI**.

> A minimal Claude Code harness: design-approval gate, destructive-command guard, verification & review workflow, and lesson memory. Nothing else.

## 설치

```
/plugin marketplace add yeschan119/claude-kiss
/plugin install kiss@claude-kiss
```

필요 조건: `python3`(3.8+), `git`. 추가 패키지는 없습니다.

팀 레포에 넣어 두려면 `.claude/settings.json` 에 다음을 추가합니다. 폴더를 신뢰하면 설치 안내가 뜹니다.

```json
{
  "extraKnownMarketplaces": {
    "claude-kiss": { "source": { "source": "github", "repo": "yeschan119/claude-kiss" } }
  },
  "enabledPlugins": { "kiss@claude-kiss": true }
}
```

## 들어 있는 것

| 구분 | 이름 | 하는 일 |
|---|---|---|
| 규칙 | `rules/RULES.md` | DRY·KISS·YAGNI, 이름·예외·모듈·로그, 검증·완료 기준, git·위험 작업 규칙. 세션 시작 때 자동 주입 |
| 스킬 | `/kiss:design` | 모드 분류 → 조사 → 설계 → **승인 게이트** → 구현 → 검증 → 완료 보고. `on/off/status` 로 게이트 조작 |
| | `/kiss:verify` | 입력·출력·예외·로그·회귀를 실행 증거로 확인하고 PASS / FAIL / INCOMPLETE 판정 |
| | `/kiss:review` | 브랜치·PR 변경분을 의도·품질·계층·데이터로 검사, 순증 기준 판정 (읽기 전용) |
| | `/kiss:learn` | 사용자 지적을 `.claude/lessons.md` 에 누적. 다음 세션에 자동 주입 |
| | `/kiss:danger` | 위험 명령 게이트 on/off (사용자만 실행) |
| | `/kiss:testfile` | 테스트 파일 커밋 게이트 on/off (사용자만 실행) |
| 에이전트 | `investigator` · `designer` · `verifier` · `reviewer` | 조사 · 모드별 설계 · 별도 레인 검증 · 리뷰 |
| 훅 | `session_start.py` | 규칙·게이트 명령·프로젝트 교훈 주입 |
| | `bash_guard.py` | 비가역 명령 차단, 테스트 파일 커밋 차단, `gh pr create --base` 강제, commit·push·PR·rm·sudo·패키지 설치·마이그레이션은 확인 |
| | `design_gate.py` | git 레포 안 코드 파일은 승인 전에 편집 차단 (`.md`·`.claude/`·`docs/` 제외) |

## 동작 방식

**설계 게이트** — 기본으로 잠겨 있습니다. Claude 는 `/kiss:design` 절차로 설계안을 보여 주고 승인을 받은 뒤 게이트를 엽니다. 게이트를 여는 명령에는 항상 확인창이 뜹니다. 간단한 수정이면 `/kiss:design on 30` 으로 직접 열고, 끝나면 `/kiss:design off` 로 잠급니다.

**차단 vs 확인**

| 등급 | 명령 | 푸는 법 |
|---|---|---|
| 차단 | `push --force`·`push +ref`, `reset --hard`, `clean`, `commit --amend`, 브랜치·태그 삭제, `checkout --`/`restore`, `rm -rf`, `docker down -v`·`prune`, `DROP`/`TRUNCATE` | `/kiss:danger on [분]` |
| 차단 | 테스트 파일(`test_*.py`, `*_test.py/go`, `*.test/spec.[jt]s(x)`, `tests/`)이 커밋에 들어감 | `/kiss:testfile on [분]` |
| 차단 | `gh pr create` 에 `--base` 없음 | `--base` 를 명시 |
| 확인 | `git commit/push/merge/rebase/reset/switch/checkout/pull…`, `gh pr create/merge`, `docker up/down…`, `rm`, `chmod`, `sudo`, 패키지 설치, 마이그레이션 | 확인창에서 허락 |

판정은 명령 **위치** 기준입니다. 커밋 메시지나 heredoc 본문에 `rm -rf` 같은 글자가 있다는 이유만으로는 막지 않습니다.

**게이트 상태**는 레포가 아니라 `~/.claude/kiss/gates/` 에 저장되고, 만료 시각이 지나면 자동으로 잠깁니다(기본 15~30분, 최대 480분). 그래서 레포에 흔적이 남지 않습니다.

**교훈**은 프로젝트의 `.claude/lessons.md` 에 쌓이고, 최근 200줄이 세션마다 주입됩니다. 팀과 공유하려면 이 파일을 커밋합니다.

## 끄기

한 레포에서만 끄려면 `.claude/settings.json` 에 `"enabledPlugins": { "kiss@claude-kiss": false }` 를 넣습니다. 완전히 지우려면 `/plugin uninstall kiss@claude-kiss` 를 실행합니다.

## License

MIT
