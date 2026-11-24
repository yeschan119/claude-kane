# claude-kane

Claude Code 를 위한 **최소 개발 하네스** 플러그인입니다. 설치하면 어느 레포에서든 같은 개발 규칙과 안전장치가 바로 적용됩니다.
기능이 많은 오케스트레이션 플러그인과 달리, 실제로 매일 쓰는 것만 남겼습니다 — **DRY · KISS · YAGNI**.

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

<details>
<summary><b>superpowers</b> — 개발 기법 스킬 모음</summary>

브레인스토밍, 계획 작성·실행, TDD, 체계적 디버깅, 완료 전 검증, 코드 리뷰 요청·수용, git worktree, 서브에이전트 병렬 작업 스킬이 들어 있습니다.

- 저장소: [obra/superpowers](https://github.com/obra/superpowers)
- 설치:
  ```
  /plugin install superpowers@claude-plugins-official
  ```

</details>

<details>
<summary><b>andrej-karpathy-skills</b> — LLM 코딩 실수를 줄이는 행동 지침</summary>

Andrej Karpathy 가 짚은 LLM 코딩 실수(과한 추상화·요청 밖 수정·가정 숨기기 등)를 줄이는 지침 스킬 1개입니다. 가볍습니다.

- 저장소: [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills)
- 설치:
  ```
  /plugin marketplace add forrestchang/andrej-karpathy-skills
  /plugin install andrej-karpathy-skills@karpathy-skills
  ```

</details>

<details>
<summary><b>playground</b> — 인터랙티브 HTML 플레이그라운드</summary>

조작 패널과 실시간 미리보기가 있는 단일 HTML 파일을 만듭니다. 결과를 프롬프트로 복사해 Claude 에게 되돌려 줄 수 있습니다.

- 저장소: [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official)
- 설치:
  ```
  /plugin install playground@claude-plugins-official
  ```

</details>

<details>
<summary><b>oh-my-claudecode</b> — 멀티 에이전트 오케스트레이션</summary>

에이전트 19개·스킬 40개(autopilot, ralph, team, deep-interview 등). 큰 작업을 자동으로 끝까지 밀고 갈 때 씁니다.

- 저장소: [Yeachan-Heo/oh-my-claudecode](https://github.com/Yeachan-Heo/oh-my-claudecode)
- 설치:
  ```
  /plugin marketplace add Yeachan-Heo/oh-my-claudecode
  /plugin install oh-my-claudecode@omc
  ```

</details>

<details>
<summary><b>eli5</b> — 듣는 사람 수준에 맞춘 설명</summary>

주제·코드·오류를 "5살에게", "매니저에게", "시니어 개발자에게"처럼 대상에 맞춰 어휘·비유·깊이를 바꿔 설명하는 스킬입니다. "ELI5", "~에게 설명해줘" 같은 말에 자동으로 켜집니다.

- 저장소: [DreambigOu/ELI5](https://github.com/DreambigOu/ELI5)
- 설치(스킬 폴더 복사):
  ```
  git clone https://github.com/DreambigOu/ELI5.git
  cp -r ELI5/skills/eli5 ~/.claude/skills/eli5
  ```

</details>

<details>
<summary><b>understand-anything</b> — 코드베이스를 인터랙티브 지식 그래프로</summary>

멀티 에이전트로 코드베이스를 분석해 탐색·검색·질문할 수 있는 지식 그래프를 만듭니다. `/understand` 로 분석, `/understand-dashboard` 로 그래프 보기, `/understand-chat`·`/understand-explain`·`/understand-onboard` 로 질문·파일 설명·온보딩 안내를 받습니다.

- 저장소: [Egonex-AI/Understand-Anything](https://github.com/Egonex-AI/Understand-Anything)
- 설치:
  ```
  /plugin marketplace add Egonex-AI/Understand-Anything
  /plugin install understand-anything
  ```

</details>

<details>
<summary><b>oh-my-mermaid</b> — 코드 전체를 Mermaid 아키텍처 다이어그램으로</summary>

코드베이스를 분석해 Mermaid 아키텍처 문서(`.omm/`)를 만들고, 브라우저 뷰어로 다이어그램을 오가며 볼 수 있습니다. Claude Code 안에서 `/omm-scan` 으로 생성, 터미널에서 `omm view` 로 확인합니다. `omm config language ko` 로 한국어 문서도 됩니다.

- 저장소: [oh-my-mermaid/oh-my-mermaid](https://github.com/oh-my-mermaid/oh-my-mermaid)
- 설치(터미널):
  ```
  npm install -g oh-my-mermaid && omm setup
  ```

</details>

<details>
<summary><b>visual-skills</b> — AI 영상·이미지 프롬프트 작성</summary>

`video`·`image` 스킬 2개. 연출·카메라·편집 규칙을 바탕으로 Seedance, Kling, Veo, Nano Banana, GPT Image 등 모델별 문법에 맞춘 프롬프트를 바로 복사해 쓸 수 있게 써 줍니다.

- 저장소: [smixs/visual-skills](https://github.com/smixs/visual-skills)
- 설치:
  ```
  /plugin marketplace add smixs/visual-skills
  /plugin install visual-skills@visual-skills
  ```

</details>

함께 쓸 때 주의할 점:

- superpowers 와 oh-my-claudecode 에도 계획·검증·리뷰 절차가 있어 kane 의 `/kane:design`·`/kane:verify`·`/kane:review` 와 겹칩니다. 한 작업에는 한쪽 절차만 쓰세요.
- oh-my-claudecode 는 무겁고(세션 컨텍스트·훅이 많음) 자율 실행 모드가 있습니다. kane 의 훅은 그대로 동작해 위험 명령은 막지만, 필요한 레포에서만 project 범위로 켜는 것을 권합니다.
- understand-anything 과 oh-my-mermaid 는 코드베이스 전체를 훑어 분석하므로 큰 레포에서는 토큰을 많이 씁니다. 처음에는 작은 레포에서 먼저 돌려 보세요.

## 추천 스킬

Claude 를 쓸 때 함께 두면 좋은 외부 스킬입니다. 모두 따로 설치하며, 설치 후에는 Claude Code 를 재시작하거나 `/reload-plugins` 를 실행합니다.

<details>
<summary><b>find-skills</b> — 필요한 스킬을 찾아 설치</summary>

"X 하는 스킬 있어?"처럼 물으면 공개 스킬 디렉터리([skills.sh](https://skills.sh))를 검색해 후보를 보여 주고, 고르면 설치합니다. 내부적으로 Skills CLI(`npx skills`)를 씁니다.

- 저장소: [vercel-labs/skills](https://github.com/vercel-labs/skills)
- 설치:
  ```
  npx skills add vercel-labs/skills --skill find-skills
  ```
- 사용법:
  - Claude 에게 "PDF 다루는 스킬 찾아줘", "is there a skill for X" 처럼 묻습니다.
  - 직접 쓸 때: `npx skills find <검색어>` 검색 · `npx skills add <owner/repo>` 설치 · `npx skills update` 업데이트
  - 기본은 현재 프로젝트에 설치되고, `-g` 를 붙이면 사용자 전체에 설치됩니다. 처음 보는 스킬은 내용을 확인한 뒤 프로젝트 범위로 설치하는 것을 권합니다.

</details>

<details>
<summary><b>claude-mem</b> — 세션 간 기억</summary>

작업하는 동안 별도 에이전트가 관찰 내용을 기록해 두고, 다음 세션 시작 때 요약 색인을 주입합니다. 세부 내용은 필요할 때만 검색해서 불러오므로 토큰을 아낍니다. 기억은 `~/.claude-mem` 에 로컬로 저장됩니다.

- 저장소: [thedotmack/claude-mem](https://github.com/thedotmack/claude-mem)
- 설치 (Claude Code 안에서):
  ```
  /plugin marketplace add thedotmack/claude-mem
  /plugin install claude-mem
  ```
  또는 터미널에서 `npx claude-mem install`. `npm install -g claude-mem` 은 라이브러리만 깔리고 훅이 등록되지 않으니 쓰지 않습니다.
- 사용법:
  - 설치 후 평소처럼 작업하면 기록이 자동으로 쌓이고, 같은 프로젝트의 다음 세션부터 기억이 주입됩니다.
  - "지난번에 인증 버그 어떻게 고쳤지?"처럼 물으면 `mem-search` 스킬이 과거 기록을 찾습니다.
  - 기록·세션·설정은 시작 때 출력되는 워커 주소의 `/viewer` 에서 봅니다.
  - 설치 중 로그인과 메모리 제공자(유료 observer 체험판, 본인 API 키, Anthropic 플랜) 선택이 나옵니다. 익명 사용 통계는 기본으로 켜져 있으며 `npx claude-mem telemetry disable` 로 끕니다.
  - kane 의 `/kane:learn` 은 사용자가 지적한 교훈만 명시적으로 남기고, claude-mem 은 작업 전체를 자동으로 기록합니다.

</details>

<details>
<summary><b>impeccable</b> — UI 디자인 다듬기 명령 모음</summary>

AI 가 만든 화면 특유의 뻔한 디자인을 피하도록 돕는 디자인 스킬입니다. 이미 있는 페이지·컴포넌트를 지목해 고칠 때 가장 잘 동작합니다. 명령 24개와 UI 파일 편집 때 자동으로 도는 디자인 검사 훅이 들어 있습니다.

- 저장소: [pbakaus/impeccable](https://github.com/pbakaus/impeccable) · 문서: [impeccable.style/docs](https://impeccable.style/docs)
- 설치:
  ```
  npx impeccable install
  ```
  설치기가 프로젝트·전역 범위와 디자인 훅 설치 여부를 묻습니다. 플러그인으로 넣으려면 `/plugin marketplace add pbakaus/impeccable` 후 `/plugin` 에서 설치합니다. 업데이트는 `npx impeccable update`.
- 사용법:
  - 프로젝트마다 한 번 `/impeccable init` → `PRODUCT.md` 생성. 기존 디자인을 `DESIGN.md` 로 남기려면 `/impeccable document`.
  - `/impeccable <명령> <대상>` 형식: 예) `/impeccable critique the pricing cards`, `/impeccable polish settings`
  - 자주 쓰는 명령: `critique`(UX 점수 리뷰) · `audit`(기술 품질 보고) · `polish`(출시 전 마무리) · `bolder`/`quieter`(강약 조절) · `harden`(에러·오버플로·엣지 케이스)
  - `/impeccable` 만 입력하면 전체 명령 목록이 나옵니다. CLI 로 `npx impeccable detect src/` 를 돌리면 CI 에서도 검사할 수 있습니다.

</details>

<details>
<summary><b>frontend-design</b> — 새 화면을 개성 있게 만들기</summary>

Anthropic 공식 스킬입니다. 새 페이지·컴포넌트를 만들 때 먼저 디자인 방향(톤·타이포·색·레이아웃)을 정하게 해서, 흔한 기본값 디자인 대신 완성도 있는 프로덕션 코드를 만들게 합니다.

- 저장소: [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official)
- 설치:
  ```
  /plugin install frontend-design@claude-plugins-official
  ```
- 사용법:
  - 따로 부르지 않아도 프론트엔드 화면을 만들어 달라고 하면 자동으로 적용됩니다. 예) "SaaS 랜딩 페이지를 만들어줘. 톤은 미니멀하고 고급스럽게"
  - 원하는 분위기·대상 사용자·제약(프레임워크, 접근성)을 함께 말하면 결과가 좋아집니다.
  - 새로 만들 때는 frontend-design, 이미 있는 화면을 다듬을 때는 impeccable 로 나눠 쓰면 겹치지 않습니다.

</details>

## 플러그인 명령어

터미널에서는 `claude plugin …`, Claude Code 안에서는 `/plugin …` 을 씁니다. 평소에는 `list`·`install`·`marketplace update`·`update`·`disable` 다섯 개면 충분합니다.

<details>
<summary><b>사용자용 — 설치·관리</b></summary>

| 명령 | 하는 일 |
|---|---|
| `claude plugin list` | 설치된 플러그인 목록, 버전, 범위, 켜짐 여부 |
| `claude plugin install <이름>@<마켓>` (`i`) | 설치. 범위는 `-s user\|project\|local` |
| `claude plugin update <이름>@<마켓>` | 최신 버전으로 업데이트. 재시작해야 반영 |
| `claude plugin uninstall <이름>@<마켓>` (`remove`) | 삭제 |
| `claude plugin enable <이름>` / `disable <이름>` | 켜기·끄기 (지우지 않음) |
| `claude plugin configure <이름>` | 플러그인 옵션 확인·설정 |
| `claude plugin prune` (`autoremove`) | 더 이상 필요 없는 자동 설치 의존성 정리 |
| `claude plugin restore-set-aside <이름>` | 조직이 마켓플레이스 출처를 바꿀 때 보관된 옵션·시크릿 복원 |

</details>

<details>
<summary><b>마켓플레이스</b></summary>

| 명령 | 하는 일 |
|---|---|
| `claude plugin marketplace add <소스>` | 등록. 소스는 GitHub `owner/repo`, URL, 로컬 경로 |
| `claude plugin marketplace list` | 등록된 마켓플레이스 목록 |
| `claude plugin marketplace update [이름]` | 카탈로그 새로고침. 이름을 생략하면 전체 |
| `claude plugin marketplace remove <이름>` (`rm`) | 등록 해제 |

</details>

<details>
<summary><b>개발자용 — 만들기·배포</b></summary>

| 명령 | 하는 일 |
|---|---|
| `claude plugin init <이름>` (`new`) | `~/.claude/skills/<이름>/` 에 새 플러그인 뼈대 생성 |
| `claude plugin validate <경로>` | `plugin.json`·마켓플레이스·스킬·에이전트 형식 검사 |
| `claude plugin details <이름>` | 구성 요소 목록과 예상 토큰 비용 (훅 주입분은 빠짐) |
| `claude plugin eval [대상]` | `evals/` 케이스로 플러그인 동작 채점 |
| `claude plugin tag [경로]` | `<이름>--v<버전>` 릴리스 태그 생성. `--dry-run`·`--push` |
| `claude plugin test [폴더]` | mod 테스트 실행 |
| `claude --plugin-dir <경로>` | 설치 없이 개발 중인 플러그인을 한 번 불러와 실행 |

</details>

<details>
<summary><b>Claude Code 안에서 — <code>/plugin</code></b></summary>

| 명령 | 하는 일 |
|---|---|
| `/plugin` | 플러그인 관리 화면 (탐색·설치·켜기·끄기) |
| `/plugin marketplace add <소스>` | 마켓플레이스 등록 |
| `/plugin install <이름>@<마켓>` | 설치 |
| `/plugin marketplace update <이름>` → `/plugin update <이름>@<마켓>` | 업데이트 순서 |
| `/plugin uninstall <이름>@<마켓>` | 삭제 |
| `/context` | 현재 세션 컨텍스트를 플러그인 등이 얼마나 차지하는지 확인 |

</details>

## License

MIT
