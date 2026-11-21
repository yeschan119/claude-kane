# claude-kane

Claude Code 를 위한 **최소 개발 하네스** 플러그인입니다. 설치하면 어느 레포에서든 같은 개발 규칙과 안전장치가 바로 적용됩니다.
기능이 많은 오케스트레이션 플러그인과 달리, 실제로 매일 쓰는 것만 남겼습니다 — **KISS · YAGNI**.

> A minimal Claude Code harness: design-approval gate, destructive-command guard, verification & review workflow, and lesson memory. Nothing else.

## 설치

```
/plugin marketplace add yeschan119/claude-kane
/plugin install kane@claude-kane
```

필요 조건: `python3`(3.8+), `git`. 추가 패키지는 없습니다.

팀 레포에 넣어 두려면 `.claude/settings.json` 에 다음을 추가합니다. 폴더를 신뢰하면 설치 안내가 뜹니다.

```json
{
  "extraKnownMarketplaces": {
    "claude-kane": { "source": { "source": "github", "repo": "yeschan119/claude-kane" } }
  },
  "enabledPlugins": { "kane@claude-kane": true }
}
```

## 들어 있는 것

| 구분 | 이름 | 하는 일 |
|---|---|---|
| 규칙 | `rules/RULES.md` | 작업 게이트, DRY·KISS·YAGNI, 검증·완료 기준, git·위험 작업, 보고. 세션 시작 때 자동 주입 |
| | `rules/STYLE.md` | 이름·구조·예외·로그 세부 기준. 주입하지 않고 designer·reviewer 가 읽음 |
| 스킬 | `/kane:design` | 모드 분류 → 조사 → 설계 → **승인 게이트** → 구현 → 검증 → 완료 보고. `on/off/status` 로 게이트 조작 |
| | `/kane:verify` | 입력·출력·예외·로그·회귀를 실행 증거로 확인하고 PASS / FAIL / INCOMPLETE 판정 |
| | `/kane:review` | 브랜치·PR 변경분을 의도·품질·계층·데이터로 검사, 순증 기준 판정 (읽기 전용) |
| | `/kane:learn` | 사용자 지적을 `.claude/lessons.md` 에 누적. 다음 세션에 자동 주입 |
| | `/kane:danger` | 위험 명령 게이트 on/off (사용자만 실행) |
| | `/kane:testfile` | 테스트 파일 커밋 게이트 on/off (사용자만 실행) |
| 에이전트 | `investigator` · `designer` · `verifier` · `reviewer` | 조사 · 모드별 설계 · 별도 레인 검증 · 리뷰 |
| 훅 | `session_start.py` | 규칙·게이트 명령·프로젝트 교훈 주입 |
| | `bash_guard.py` | 비가역 명령 차단, 테스트 파일 커밋 차단, `gh pr create --base` 강제, commit·push·PR·rm·sudo·패키지 설치·마이그레이션은 확인 |
| | `design_gate.py` | git 레포 안 코드 파일은 승인 전에 편집 차단 (`.md`·`.claude/`·`docs/` 제외) |

## 동작 방식

**설계 게이트** — 기본으로 잠겨 있습니다. Claude 는 `/kane:design` 절차로 설계안을 보여 주고 승인을 받은 뒤 게이트를 엽니다. 게이트를 여는 명령에는 항상 확인창이 뜹니다. 간단한 수정이면 `/kane:design on 30` 으로 직접 열고, 끝나면 `/kane:design off` 로 잠급니다.

**차단 vs 확인**

| 등급 | 명령 | 푸는 법 |
|---|---|---|
| 차단 | `push --force`·`push +ref`, `reset --hard`, `clean`, `commit --amend`, 브랜치·태그 삭제, `checkout --`/`restore`, `rm -rf`, `docker down -v`·`prune`, `DROP`/`TRUNCATE` | `/kane:danger on [분]` |
| 차단 | 테스트 파일(`test_*.py`, `*_test.py/go`, `*.test/spec.[jt]s(x)`, `tests/`)이 커밋에 들어감 | `/kane:testfile on [분]` |
| 차단 | `gh pr create` 에 `--base` 없음 | `--base` 를 명시 |
| 확인 | `git commit/push/merge/rebase/reset/switch/checkout/pull…`, `gh pr create/merge`, `docker up/down…`, `rm`, `chmod`, `sudo`, 패키지 설치, 마이그레이션 | 확인창에서 허락 |

판정은 명령 **위치** 기준입니다. 커밋 메시지나 heredoc 본문에 `rm -rf` 같은 글자가 있다는 이유만으로는 막지 않습니다.

**게이트 상태**는 레포가 아니라 `~/.claude/kane/gates/` 에 저장되고, 만료 시각이 지나면 자동으로 잠깁니다(기본 15~30분, 최대 480분). 그래서 레포에 흔적이 남지 않습니다.

**교훈**은 프로젝트의 `.claude/lessons.md` 에 쌓이고, 최근 200줄이 세션마다 주입됩니다. 팀과 공유하려면 이 파일을 커밋합니다.

## 세션 비용

| 항목 | 토큰 | 측정 |
|---|---|---|
| 세션마다 고정 | 약 2,200 | `claude -p` 입력 토큰을 플러그인 있을 때와 없을 때 비교 (27,283 → 29,463) |
| ㄴ 스킬·에이전트 목록 | 약 1,060 | `claude --plugin-dir . plugin details kane` |
| ㄴ 규칙 주입 (SessionStart) | 약 1,100 | 위 둘의 차이. `RULES.md` 만 주입하고 `STYLE.md` 는 에이전트가 필요할 때 읽음. `.claude/lessons.md` 가 있으면 그만큼 늘어남 |
| 호출할 때마다 | 220 ~ 1,500 | 스킬·에이전트별 (`plugin details` 참고) |

## 릴리스

버전은 `plugin.json` 과 `marketplace.json` 두 곳에 있고, 둘이 같아야 한다.

1. 두 파일의 `version` 을 함께 올리고 커밋·push 한다 (버전이 그대로면 설치한 쪽에서 업데이트로 잡히지 않는다)
2. `claude plugin validate .`
3. `claude plugin tag . --dry-run` 으로 확인한 뒤 `claude plugin tag . --push` — 두 버전이 다르면 여기서 거부된다
4. 설치한 쪽: `/plugin marketplace update claude-kane` → `/plugin update kane@claude-kane` → 재시작

태그 이름은 `kane--v<버전>` 이다.

## 끄기

한 레포에서만 끄려면 `.claude/settings.json` 에 `"enabledPlugins": { "kane@claude-kane": false }` 를 넣습니다. 완전히 지우려면 `/plugin uninstall kane@claude-kane` 를 실행합니다.

## 추천 플러그인

kane 은 규칙과 안전장치만 다룹니다. 아래는 필요할 때 함께 쓸 만한 플러그인입니다. 모두 따로 설치합니다.

| 플러그인 | 설명 | 설치 |
|---|---|---|
| [superpowers](https://github.com/obra/superpowers) | 개발 기법 스킬 모음 — 브레인스토밍, 계획 작성·실행, TDD, 체계적 디버깅, 완료 전 검증, 코드 리뷰 요청·수용, git worktree, 서브에이전트 병렬 작업 | `/plugin install superpowers@claude-plugins-official` |
| [andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills) | Andrej Karpathy 가 짚은 LLM 코딩 실수(과한 추상화·요청 밖 수정·가정 숨기기 등)를 줄이는 행동 지침 스킬 1개. 가볍다 | `/plugin marketplace add forrestchang/andrej-karpathy-skills`<br>`/plugin install andrej-karpathy-skills@karpathy-skills` |
| [playground](https://github.com/anthropics/claude-plugins-official) | 조작 패널과 실시간 미리보기가 있는 단일 HTML 플레이그라운드를 만든다. 결과를 프롬프트로 복사해 Claude 에게 되돌려 줄 수 있다 | `/plugin install playground@claude-plugins-official` |
| [oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode) | 멀티 에이전트 오케스트레이션 — 에이전트 19개·스킬 40개(autopilot, ralph, team, deep-interview 등). 큰 작업을 자동으로 끝까지 밀고 갈 때 | `/plugin marketplace add Yeachan-Heo/oh-my-claudecode`<br>`/plugin install oh-my-claudecode@omc` |

함께 쓸 때 주의할 점:

- superpowers 와 oh-my-claudecode 에도 계획·검증·리뷰 절차가 있어 kane 의 `/kane:design`·`/kane:verify`·`/kane:review` 와 겹칩니다. 한 작업에는 한쪽 절차만 쓰세요.
- oh-my-claudecode 는 무겁고(세션 컨텍스트·훅이 많음) 자율 실행 모드가 있습니다. kane 의 훅은 그대로 동작해 위험 명령은 막지만, 필요한 레포에서만 project 범위로 켜는 것을 권합니다.

## License

MIT
