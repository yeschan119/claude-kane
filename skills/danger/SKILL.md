---
name: danger
description: 위험 명령 게이트 — 강제 푸시·reset --hard·rm -rf·DROP 같은 비가역 명령을 한시적으로 허용하거나 잠근다. 사용자만 실행한다.
argument-hint: "on [분] | off | status"
disable-model-invocation: true
---

# /kiss:danger

인자: `$ARGUMENTS`

세션 컨텍스트의 게이트 명령으로 `danger $ARGUMENTS` 를 실행한다. 인자가 없으면 `danger status`. 출력만 전하고 다른 명령과 묶지 않는다.

열려 있는 동안에도 비가역 명령 하나하나에 대해 실행 전에 영향·복구 방법을 먼저 말한다. 작업이 끝나면 바로 `/kiss:danger off` 를 권한다. 기본 15분, 최대 480분.
