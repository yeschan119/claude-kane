---
name: testfile
description: 테스트 파일 커밋 게이트 — 테스트 파일(test_*.py, *.test.ts, tests/ 등)을 커밋에 넣는 것을 한시적으로 허용하거나 잠근다. 사용자만 실행한다.
argument-hint: "on [분] | off | status"
disable-model-invocation: true
---

# /kiss:testfile

인자: `$ARGUMENTS`

세션 컨텍스트의 게이트 명령으로 `testfile $ARGUMENTS` 를 실행한다. 인자가 없으면 `testfile status`. 출력만 전하고 다른 명령과 묶지 않는다.

열기 전에 커밋할 테스트 파일 목록·줄 수·이유가 사용자에게 보고됐어야 한다. 커밋이 끝나면 `/kiss:testfile off` 를 권한다. 기본 15분, 최대 480분.
