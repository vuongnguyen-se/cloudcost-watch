# Initial Prompt for the Coding Agent (Orca)

Copy everything below the line into Orca as the first message of a new session.

---

You are helping me build **CloudCost Watch**, a portfolio project: a FinOps platform on **Amazon EKS** that imports my AWS cost data, shows where the money goes, finds wasted resources, and alerts on cost spikes. It is the third project on my CV for an **AWS internship at SoftwareOne** (a company that sells cloud cost optimization, migration and managed services), so it must look and behave like a real production system, not a lab.

This repository started as `eks-platform-lab`: a working EKS platform (Terraform, Kubernetes manifests, CI/CD) running a placeholder "notes" API. We are now turning it into CloudCost Watch.

First, read every Markdown file in the project root. Treat them as the source of truth, in this order:

1. `CURRENT_STATE.md`: what exists today, what was verified, environment notes
2. `AI_CODING_RULES.md`: how to work in this repo
3. `PROJECT_REQUIREMENTS.md`: purpose, users, features, out of scope
4. `ARCHITECTURE.md`: target architecture and repository layout
5. `DATABASE_DESIGN.md`, `API_SPECIFICATION.md`
6. `SECURITY_AND_COST.md`
7. `DECISIONS.md`: decisions already made (D-xxx); do not reopen them without a reason
8. `TASKS.md`: the task board; the next task is the first unticked one

## Your first assignment

Do not build the application yet.

1. Inspect the repository and report what already exists, compared with `CURRENT_STATE.md`.
2. Compare it with the target layout in `ARCHITECTURE.md` and list the gaps.
3. Point out contradictions or missing decisions in the docs.
4. Propose the plan for **Phase 0** and **Phase 1** in `TASKS.md`, as small increments.
5. Do not create AWS resources, deploy anything, or rename the GitHub repository yet.
6. Ask me to approve the plan before making broad changes.

## Teaching expectations

I am learning cloud and Kubernetes while I build this. Explain decisions in a practical, beginner-friendly way: what each AWS service or Kubernetes object does, and how requests and data flow between them.

When I approve implementation, work in small increments. For each increment:
- State the objective and the task ID from `TASKS.md`.
- List the files you will create or change.
- Implement the smallest useful change, with tests.
- Tell me how to run and verify it.
- Update `TASKS.md` and `CURRENT_STATE.md`.

Never claim code, tests, AWS resources or deployments succeeded unless you actually verified them. Ask before any step marked 💰 (creates billable AWS resources).
