<a id="top"></a>

<div align="center">

<img src="./assets/hero.svg" width="100%" alt="강다니엘 — T0C0-AI · 솔로 메이커 · 바이브코더" />

<br><br>

<a href="https://blog.naver.com/ejdnjs0930"><img src="https://img.shields.io/badge/BLOG-강다니엘의%20개발일지-03C75A?style=for-the-badge&logo=naver&logoColor=white&labelColor=000000" alt="네이버 블로그" /></a>
<a href="mailto:ejdnjs0930@gmail.com"><img src="https://img.shields.io/badge/MAIL-ejdnjs0930@gmail.com-D14836?style=for-the-badge&logo=gmail&logoColor=white&labelColor=000000" alt="이메일" /></a>
<img src="https://komarev.com/ghpvc/?username=T0C0-AI&style=for-the-badge&color=yellow&label=PROFILE+VIEWS" alt="프로필 조회수" />

</div>

<img src="./assets/divider.svg" width="100%" alt="" />

<br>

<div align="center">

## ⚡ whoami

<img src="./assets/terminal.svg" width="880" alt="터미널: whoami — 강다니엘, 1인 프로덕트 메이커 · 바이브코더" />

</div>

<br>

## 🐧 TOCO UNIVERSE

> 토코(TOCO)는 펭귄+고양이 AI 캐릭터이자, 내가 만드는 모든 것의 구심점.
> 하나의 캐릭터를 중심으로 영상 파이프라인 → 에이전트 → 인텔리전스 → 라이프까지 확장 중.

```mermaid
%%{init: {'theme':'base','themeVariables':{'primaryColor':'#FFE600','primaryTextColor':'#000000','primaryBorderColor':'#000000','lineColor':'#FFE600','fontFamily':'monospace','mainBkg':'#FFE600','edgeLabelBackground':'#0d0d0d','clusterBkg':'#111111','clusterBorder':'#FFE600','tertiaryTextColor':'#ffffff'}}}%%
flowchart LR
    TOCO(["🐧 TOCO<br/>펭귄 + 고양이 AI"])

    TOCO --> V["🎬 영상 파이프라인"]
    TOCO --> A["🤖 에이전트"]
    TOCO --> I["📈 인텔리전스"]
    TOCO --> L["🧭 라이프 & 시티"]

    V --> V1["toko-creator<br/>AI 숏폼 자동 생성"]
    V --> V2["toco-dubbing<br/>영상 → 한국어 자막 MP4"]
    V --> V3["즉석자막<br/>실시간 자막 데스크톱 앱"]

    A --> A1["Orchestrator<br/>에이전트 배포 지휘"]
    A --> A2["dn8-assistant<br/>차량 AI 비서"]
    A --> A3["claude-pet<br/>데스크톱 펫 에이전트"]

    I --> I1["Stockmind<br/>개인 투자 두뇌"]
    I --> I2["opportunity-os<br/>AI Sales Agent"]
    I --> I3["gapminer<br/>1인 제품 기회 발굴"]

    L --> L1["tocosteps<br/>추억 동선 아카이브"]
    L --> L2["Real-Proceedings<br/>AI 회의록"]
    L --> L3["Changwon-Digital-Twin<br/>도시 디지털 트윈"]
```

<br>

## 🚀 지금 만들고 있는 것들

> 대부분 🔒 private — 솔로 메이커의 실험실은 원래 문이 닫혀 있다. 완성되면 하나씩 공개.

| 프로젝트 | 무엇을 하는 물건인가 | 스택 | 상태 |
|---|---|---|---|
| 🗺 **tocosteps** | 사진만 올리면 한국 지도 위에 추억 동선이 자동으로 그려지고, 스크롤하면 영화처럼 재생되는 추억 아카이브 | `TypeScript` | 🔒 빌드 중 |
| 🧠 **Stockmind** | 한국 주식을 AI가 분석·시뮬레이션하고 내 매매를 복기해 주는, 나 혼자 쓰는 투자 두뇌 — 단정 금지, 확률과 근거만 | `TypeScript` | 🔒 운용 중 |
| 🤖 **Orchestrator** | 오케스트레이터의 지시로 프로젝트에 필요한 에이전트를 배포하는 멀티 에이전트 플러그인 | `JavaScript` | 🔒 연구 중 |
| 🚗 **dn8-assistant** | Hyundai Developers 공식 API 기반 — 내 차(DN8)의 상태·연비·정비·출발 브리핑을 챙기는 AI 차량 비서 | `Python` | 🔒 빌드 중 |
| 🎬 **toko-creator** | 토코 캐릭터가 진행하는 AI 숏폼 자동 생성 시스템 | `Python` | 🔒 빌드 중 |
| 🎙 **Real-Proceedings** | 실시간 STT + 화자 분리 + 끝나면 AI 요약까지, 개인용 회의록 앱 | `TypeScript` | 🔒 빌드 중 |
| 🏙 **Changwon-Digital-Twin** | 창원시 데이터를 3D 지도에 올리고 교통·날씨·대기질·재난을 실시간 패널로 — 로컬 우선 디지털 트윈 | `TypeScript` | 🔒 빌드 중 |
| 🕵 **opportunity-os** | 기업 이벤트를 감지(Signal) → 추론(Reasoning) → 행동(Action)하는 Event Intelligence · AI Sales Agent | `TypeScript` | 🔒 설계 중 |

<details>
<summary><b>🧪 실험실 더 보기 (+12)</b></summary>

<br>

| 프로젝트 | 한 줄 | 스택 |
|---|---|---|
| 🎞 **toco-dubbing** | 영상 드래그 또는 URL만으로 한국어 자막 합성 MP4 자동 생성 | `Python` |
| 💬 **jeukseok-jamak-window** | 즉석자막 — 실시간 자막 Windows 데스크톱 앱 (Tauri) | `Python` |
| 🇯🇵 **jp-ko-subtitle-mac** | 일본어/영어 소리를 듣고 한국어 자막을 만드는 도구 | `Python` |
| 🧽 **subtitle-eraser** | 영상에 박힌 자막을 지우는 도구 | `Python` |
| ⚽ **player-tracker** | YouTube 축구 영상 YOLO 선수 추적 분석 | `JavaScript` |
| 💡 **idea-feed** | Threads·Instagram 아이디어 포스트 자동 수집 + Claude 초안 생성 대시보드 | `JavaScript` |
| ⛏ **gapminer** | 사용자 불만 신호를 크롤링해 1~3일짜리 1인 제품 기회를 발굴·점수화 | `HTML/JS` |
| 🔐 **sentinel-mac** | 맥북 분실·도난 대응 개인 보안 추적 플랫폼 | `TypeScript` |
| 🐱 **claude-pet** | 데스크톱에 사는 Claude 펫 | `Python` |
| 🖼 **webtoon-studio** | 웹툰 제작 스튜디오 실험 | `TypeScript` |
| ✨ **TocoEffects** | 토코 영상용 이펙트 모음 | `HTML` |
| 🏠 **Portfolio-Home** | 강다니엘의 포트폴리오 홈 | `HTML` |

</details>

<br>

## 🛠️ 기술 스택

<div align="center">

<img src="https://skillicons.dev/icons?i=ts,js,py,cpp,nodejs,react,nextjs,tauri,tailwind,fastapi,docker,githubactions,git,github,postgres,redis,figma,vscode,linux,bash,vercel,aws&perline=11&theme=dark" alt="기술 스택 아이콘" />

<br><br>

<img src="https://img.shields.io/badge/Neo--Brutalism-Design_Style-FFE600?style=for-the-badge&labelColor=000000" alt="Neo-Brutalism Design Style" />
<img src="https://img.shields.io/badge/Claude_Code-Daily_Driver-FFE600?style=for-the-badge&logo=anthropic&logoColor=black&labelColor=000000" alt="Claude Code" />

</div>

<br>

<img src="./assets/divider.svg" width="100%" alt="" />

<!-- ACTIVITY-TELEMETRY:START -->

<div align="center">

<h3>🕐 시간대별 커밋 활동</h3>
<sub>전체 누적</sub>

<img src="https://img.shields.io/badge/%EC%A0%84%EC%B2%B4_%EC%BB%A4%EB%B0%8B-8,868-ffffff?style=for-the-badge&logo=git&logoColor=white" />
<img src="https://img.shields.io/badge/%EB%88%84%EC%A0%81_%EC%BB%A4%EB%B0%8B-7749-bd00ff?style=for-the-badge&logo=github&logoColor=white" />
<img src="https://img.shields.io/badge/%EC%BD%94%EB%93%9C_%EB%A6%AC%EB%B7%B0-1-06b6d4?style=for-the-badge&logo=codereview&logoColor=white" />

<br><br>

<table><tr>
<td align="center" valign="top">
<picture>
  <img src="./assets/activity-telemetry.svg" width="420" />
</picture>
</td>
<td align="center" valign="top">
<picture>
  <img src="./assets/overall-activity.svg" width="420" />
</picture>
</td>
</tr></table>

<br>

<sub>마지막 갱신: 2026-07-03 01:00 KST · GitHub Actions 자동 생성</sub>

</div>

<!-- ACTIVITY-TELEMETRY:END -->

<br>

<div align="center">

## 🐍 잔디 먹는 뱀

<sub>잔디의 대부분은 private 레포에 숨어 있다 — 뱀은 보이는 것만 먹는다.</sub>

<br><br>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/T0C0-AI/T0C0-AI/output/snake-dark.svg" />
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/T0C0-AI/T0C0-AI/output/snake.svg" />
  <img src="https://raw.githubusercontent.com/T0C0-AI/T0C0-AI/output/snake-dark.svg" width="100%" alt="컨트리뷰션 그래프를 먹는 뱀" />
</picture>

</div>

<br>

## ⚑ 원칙

```text
[01] 배포되지 않은 코드는 존재하지 않는 코드다.
[02] AI는 도구가 아니라 팀원이다. 나는 지휘자다.
[03] 혼자서도 팀의 속도를 낸다 — 그게 솔로 메이커의 증명.
[04] 직각 모서리, 검정과 노랑. Neo-Brutalism.
```

<img src="./assets/divider.svg" width="100%" alt="" />

<div align="center">
<br>
<sub>이 페이지의 히어로 · 터미널 · 디바이더는 라이브러리 없이 손으로 만든 애니메이션 SVG입니다 ✋🐧</sub>
<br>
<sub>텔레메트리는 매일 00:00 KST, 뱀은 00:10 KST에 GitHub Actions가 자동 갱신</sub>
<br><br>
<a href="#top"><img src="https://img.shields.io/badge/⬆_맨_위로-FFE600?style=for-the-badge&labelColor=000000" alt="맨 위로" /></a>
<br><br>
</div>
