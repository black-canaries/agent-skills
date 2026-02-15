> **Note:** This repository contains Anthropic's implementation of skills for Claude. For information about the Agent Skills standard, see [agentskills.io](http://agentskills.io).

# Skills
Skills are folders of instructions, scripts, and resources that Claude loads dynamically to improve performance on specialized tasks. Skills teach Claude how to complete specific tasks in a repeatable way, whether that's creating documents with your company's brand guidelines, analyzing data using your organization's specific workflows, or automating personal tasks.

For more information, check out:
- [What are skills?](https://support.claude.com/en/articles/12512176-what-are-skills)
- [Using skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude)
- [How to create custom skills](https://support.claude.com/en/articles/12512198-creating-custom-skills)
- [Equipping agents for the real world with Agent Skills](https://anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

# About This Repository

This repository contains skills that demonstrate what's possible with Claude's skills system. These skills range from creative applications (art, music, design) to technical tasks (testing web apps, MCP server generation) to enterprise workflows (communications, branding, etc.).

Each skill is self-contained in its own folder with a `SKILL.md` file containing the instructions and metadata that Claude uses. Browse through these skills to get inspiration for your own skills or to understand different patterns and approaches.

Many skills in this repo are open source (Apache 2.0). We've also included the document creation & editing skills that power [Claude's document capabilities](https://www.anthropic.com/news/create-files) under the hood in the [`skills/docx`](./skills/docx), [`skills/pdf`](./skills/pdf), [`skills/pptx`](./skills/pptx), and [`skills/xlsx`](./skills/xlsx) subfolders. These are source-available, not open source, but we wanted to share these with developers as a reference for more complex skills that are actively used in a production AI application.

## Disclaimer

**These skills are provided for demonstration and educational purposes only.** While some of these capabilities may be available in Claude, the implementations and behaviors you receive from Claude may differ from what is shown in these skills. These skills are meant to illustrate patterns and possibilities. Always test skills thoroughly in your own environment before relying on them for critical tasks.

# Skill Sets

- [./spec](./spec): The Agent Skills specification
- [./template](./template): Skill template

## Creative & Design
| Skill | Description |
|-------|-------------|
| [algorithmic-art](./skills/algorithmic-art) | Creating algorithmic art using p5.js with seeded randomness and interactive parameter exploration |
| [brand-guidelines](./skills/brand-guidelines) | Applies Anthropic's official brand colors and typography to artifacts |
| [canvas-design](./skills/canvas-design) | Create visual art in .png and .pdf documents using design philosophy |
| [frontend-design](./skills/frontend-design) | Create distinctive, production-grade frontend interfaces with high design quality |
| [theme-factory](./skills/theme-factory) | Toolkit for styling artifacts with 10 pre-set themes or custom on-the-fly generation |

## Expo & React Native
| Skill | Description |
|-------|-------------|
| [building-native-ui](./skills/building-native-ui) | Complete guide for building beautiful apps with Expo Router — styling, components, navigation, animations, and native tabs |
| [eas](./skills/eas) | Build, submit, and update React Native/Expo apps using EAS (Expo Application Services) |
| [expo-api-routes](./skills/expo-api-routes) | Guidelines for creating API routes in Expo Router with EAS Hosting |
| [expo-cicd-workflows](./skills/expo-cicd-workflows) | Write EAS workflow YAML files for Expo CI/CD pipelines and deployment automation |
| [expo-deployment](./skills/expo-deployment) | Deploying Expo apps to iOS App Store, Android Play Store, web hosting, and API routes |
| [expo-dev-client](./skills/expo-dev-client) | Build and distribute Expo development clients locally or via TestFlight |
| [expo-swift-ui](./skills/expo-swift-ui) | Build native iOS interfaces with SwiftUI components through Expo SDK 55's @expo/ui package |
| [maestro-tests](./skills/maestro-tests) | Write and run Maestro E2E tests for React Native Expo apps |
| [native-data-fetching](./skills/native-data-fetching) | Implement network requests, API calls, caching strategies, and offline support |
| [use-dom](./skills/use-dom) | Use Expo DOM components to run web code in a webview on native and as-is on web |

## Backend & Full-Stack
| Skill | Description |
|-------|-------------|
| [convex](./skills/convex) | Build full-stack applications with Convex — real-time queries, mutations, actions, agents, RAG, workflows, and auth |
| [convex-agents](./skills/convex-agents) | Build AI agents on Convex with persistent chat history, durable workflows, tool calling, streaming, and RAG |

## Desktop & Cross-Platform
| Skill | Description |
|-------|-------------|
| [tauri](./skills/tauri) | Build cross-platform desktop and mobile applications with Tauri v2 |

## Native iOS
| Skill | Description |
|-------|-------------|
| [swiftui-expert-skill](./skills/swiftui-expert-skill) | Write, review, or improve SwiftUI code following best practices for state management, performance, and iOS 26+ Liquid Glass |

## Document Skills
| Skill | Description |
|-------|-------------|
| [docx](./skills/docx) | Create, read, edit, and manipulate Word documents (.docx files) |
| [pdf](./skills/pdf) | Read, create, merge, split, encrypt, OCR, and manipulate PDF files |
| [pptx](./skills/pptx) | Create, read, edit, and manipulate PowerPoint presentations (.pptx files) |
| [xlsx](./skills/xlsx) | Create, read, edit, and manipulate spreadsheet files (.xlsx, .csv, .tsv) |

## Enterprise & Communication
| Skill | Description |
|-------|-------------|
| [doc-coauthoring](./skills/doc-coauthoring) | Structured workflow for co-authoring documentation, proposals, and technical specs |

## Development & Technical
| Skill | Description |
|-------|-------------|
| [skill-creator](./skills/skill-creator) | Guide for creating effective skills that extend Claude's capabilities |
| [webapp-testing](./skills/webapp-testing) | Test local web applications using Playwright with screenshots and browser logs |

# Try in Claude Code, Claude.ai, and the API

## Claude.ai

These example skills are all already available to paid plans in Claude.ai. 

To use any skill from this repository or upload custom skills, follow the instructions in [Using skills in Claude](https://support.claude.com/en/articles/12512180-using-skills-in-claude#h_a4222fa77b).

## Claude API

You can use Anthropic's pre-built skills, and upload custom skills, via the Claude API. See the [Skills API Quickstart](https://docs.claude.com/en/api/skills-guide#creating-a-skill) for more.

# Creating a Basic Skill

Skills are simple to create - just a folder with a `SKILL.md` file containing YAML frontmatter and instructions. You can use the **template-skill** in this repository as a starting point:

```markdown
---
name: my-skill-name
description: A clear description of what this skill does and when to use it
---

# My Skill Name

[Add your instructions here that Claude will follow when this skill is active]

## Examples
- Example usage 1
- Example usage 2

## Guidelines
- Guideline 1
- Guideline 2
```

The frontmatter requires only two fields:
- `name` - A unique identifier for your skill (lowercase, hyphens for spaces)
- `description` - A complete description of what the skill does and when to use it

The markdown content below contains the instructions, examples, and guidelines that Claude will follow. For more details, see [How to create custom skills](https://support.claude.com/en/articles/12512198-creating-custom-skills).

# Partner Skills

Skills are a great way to teach Claude how to get better at using specific pieces of software. As we see awesome example skills from partners, we may highlight some of them here:

- **Notion** - [Notion Skills for Claude](https://www.notion.so/notiondevs/Notion-Skills-for-Claude-28da4445d27180c7af1df7d8615723d0)
