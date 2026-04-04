<a id="top"></a>

<picture>
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0d0d0d,3b0764,7c3aed,06b6d4&height=230&text=T0C0%20AI&fontSize=72&fontColor=ffffff&fontAlignY=42&desc=AI%20Agent%20Orchestration%20Platform&descSize=20&descAlignY=62&section=header&animation=fadeIn" width="100%" />
</picture>

<div align="center">

[![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&weight=700&size=20&duration=2800&pause=900&color=BD00FF&center=true&vCenter=true&width=750&lines=AI+에이전트가+팀으로+움직입니다;실시간+멀티+에이전트+오케스트레이션;자율+판단+%E2%80%A2+협업+%E2%80%A2+자동화;Orchestrate+the+Future+with+T0C0)](https://github.com/T0C0-AI)

<br/>

[![GitHub](https://img.shields.io/badge/GitHub-T0C0--AI-bd00ff?style=flat-square&logo=github&logoColor=white)](https://github.com/T0C0-AI)
&nbsp;
[![Blog](https://img.shields.io/badge/Blog-강다니엘의%20개발일지-03C75A?style=flat-square&logo=naver&logoColor=white)](https://blog.naver.com/ejdnjs0930)
&nbsp;
[![Email](https://img.shields.io/badge/Contact-ejdnjs0930@gmail.com-ff0080?style=flat-square&logo=gmail&logoColor=white)](mailto:ejdnjs0930@gmail.com)

</div>

---

<div align="center">

### ⚡ 하나의 AI가 아닌, **팀으로 움직이는 AI**

*에이전트들이 서로 소통하고, 스스로 판단하고, 협업으로 문제를 해결하는 오케스트레이션 플랫폼*

</div>

---

## 🧠 에이전트 도메인

<div align="center">

| 🔌 Orchestration | 🧠 Intelligence | ⚡ Automation |
|:---:|:---:|:---:|
| 멀티 에이전트 배포 & 지시 | 문서 RAG & 지식 시스템 | Notion / Slack / Discord |
| 에이전트 간 메시지 라우팅 | 회의 전사 & 다국어 통역 | macOS 데스크톱 자동화 |
| 실시간 작업 위임 & 조율 | 패턴 학습 & 자율 개선 | 이벤트 기반 트리거 |

| 🛡️ Security | 🔬 Visibility | 🚀 Platform |
|:---:|:---:|:---:|
| 생체인식 & 안면인식 보안 | 팀 활동 모니터링 | 레시피 기반 자동 설정 |
| 에이전트 격리 실행 | 실시간 대시보드 | CI/CD 자동 배포 |
| 세밀한 권한 관리 | 드리프트 감지 & 알림 | MCP 서버 통합 |

</div>

---

## 🚀 미션 스테이터스

| 에이전트 | 역할 | 상태 |
|:---|:---|:---:|
| **🔌 Orchestrator** | 에이전트 배포, 작업 지시, 멀티 에이전트 협업 | 🟢 운영중 |
| **🎙️ Voice** | 회의 전사, 실시간 다국어 동시통역 | 🟢 운영중 |
| **🖥️ Computer** | macOS 데스크톱 자동화 및 UI 제어 | 🟢 운영중 |
| **📚 RAG** | 개인 문서 인덱싱, 시맨틱 검색, 지식 관리 | 🟢 운영중 |
| **🧪 Recipe** | 프로젝트 분석, 자동 레시피 생성 & 드리프트 감지 | 🟢 운영중 |
| **⚡ Automation** | Notion, Slack, Discord 이벤트 자동화 | 🟢 운영중 |
| **👁️ Recognition** | 제스처 인식, 안면인식 보안 시스템 | 🟡 개발중 |
| **📊 Visibility** | 팀 활동 모니터링, 실시간 대시보드 | 🟡 개발중 |

---

## 📂 아키텍처 레이어

<details>
<summary><b>🔌 Orchestration Layer — 에이전트 배포 & 협업</b></summary>
<br/>

토코의 핵심 레이어. 모든 에이전트의 생명주기를 관리하고, 작업을 분배하며, 에이전트 간 메시지 라우팅을 처리합니다.

- **Dispatcher** — 자연어 명령을 분석해 적절한 에이전트에 위임
- **Architect** — 크로스커팅 관심사 식별 + 시스템 제약 정의 (Opus, 읽기 전용)
- **Worker** — Design / Implement / Review / Debug 전문화 에이전트 4종
- **Verifier** — 독립 검증, 구현 완료 후 품질 게이트
- **Tracer** — 실패 진단, OMC tracer 래퍼

```
User → Dispatcher → [Architect] → Worker × N → Verifier / Tracer
```

</details>

<details>
<summary><b>🎙️ Voice Layer — 음성 인식 & 통역</b></summary>
<br/>

실시간 음성 처리 파이프라인. 회의 전사부터 다국어 동시통역까지 처리합니다.

- **Transcription** — Whisper 기반 실시간 음성 → 텍스트
- **Translation** — 다국어 실시간 통역 (한 / 영 / 일 / 중)
- **Meeting Assistant** — 회의록 자동 생성, 요약, 액션 아이템 추출

</details>

<details>
<summary><b>🖥️ Computer Layer — 데스크톱 자동화</b></summary>
<br/>

macOS 네이티브 API를 통한 UI 자동화. 사람처럼 화면을 보고 조작합니다.

- **Screen Capture** — 실시간 화면 캡처 및 OCR
- **UI Control** — 클릭, 타이핑, 드래그, 스크롤 자동화
- **App Integration** — 앱 간 데이터 흐름 자동화

</details>

<details>
<summary><b>📚 RAG Layer — 지식 & 문서 시스템</b></summary>
<br/>

개인 및 팀의 지식을 인덱싱하고 시맨틱 검색으로 에이전트에게 컨텍스트를 제공합니다.

- **Indexing** — PDF, Notion, Markdown 문서 벡터화
- **Semantic Search** — 의미 기반 유사도 검색
- **Knowledge Graph** — 문서 간 관계 맵핑 및 추론

</details>

<details>
<summary><b>🧪 Recipe Layer — 프로젝트 자동 설정</b></summary>
<br/>

기존 프로젝트를 분석해 레시피 문서를 생성하고, 코드와 문서 간 드리프트를 감지합니다.

- **recipe-analyze** — 프로젝트 분석 후 부족한 레시피 보완
- **drift-check** — 레시피 문서와 실제 코드 간 드리프트 감지
- **scaffold** — 레시피 기반 코드 보일러플레이트 자동 생성
- **pr-guard** — PR 변경사항이 레시피 문서와 일치하는지 검증

</details>

---

## 📊 GitHub 통계

<div align="center">

<img src="https://github-readme-stats.vercel.app/api?username=T0C0-AI&show_icons=true&hide_border=true&bg_color=0d0d0d&title_color=bd00ff&icon_color=06b6d4&text_color=e2e8f0&ring_color=7c3aed" width="48%" />
&nbsp;
<img src="https://github-readme-stats.vercel.app/api/top-langs/?username=T0C0-AI&layout=compact&hide_border=true&bg_color=0d0d0d&title_color=bd00ff&text_color=e2e8f0" width="48%" />

<br/><br/>

<img src="https://streak-stats.demolab.com?user=T0C0-AI&hide_border=true&background=0d0d0d&ring=bd00ff&fire=ff0080&currStreakLabel=06b6d4&sideLabels=e2e8f0&dates=9ca3af&sideNums=bd00ff&currStreakNum=ffffff" width="60%" />

</div>

---

## 🛠️ 기술 스택

**Language**

![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)
![Rust](https://img.shields.io/badge/Rust-CE422B?style=flat-square&logo=rust&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Zig](https://img.shields.io/badge/Zig-F7A41D?style=flat-square&logo=zig&logoColor=white)

**Runtime & Framework**

![Node.js](https://img.shields.io/badge/Node.js-339933?style=flat-square&logo=node.js&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react&logoColor=black)
![Electron](https://img.shields.io/badge/Electron-47848F?style=flat-square&logo=electron&logoColor=white)

**AI & Platform**

![Claude AI](https://img.shields.io/badge/Claude%20AI-191919?style=flat-square&logo=anthropic&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-2088FF?style=flat-square&logo=github-actions&logoColor=white)
![macOS](https://img.shields.io/badge/macOS-000000?style=flat-square&logo=apple&logoColor=white)

---

## ⚖️ 철학

<div align="center">

> *"에이전트는 도구가 아니라 동료다."*

> *"자동화는 사람을 대체하지 않는다. 사람이 더 중요한 일에 집중하게 한다."*

> *"팀으로 일하는 AI가, 혼자인 AI보다 강하다."*

</div>

---

<picture>
  <img src="https://capsule-render.vercel.app/api?type=waving&color=06b6d4,7c3aed,3b0764,0d0d0d&height=130&section=footer&reversal=true" width="100%" />
</picture>

<div align="center">

🟢 **System Nominal** &nbsp;|&nbsp; 🤖 **Agents Online** &nbsp;|&nbsp; ⚡ **Orchestration Active**

**Made with 🔮 by 강다니엘** | K-Studio

[↑ 맨 위로](#top)

</div>
