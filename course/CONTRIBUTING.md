# Contributing to the Marketplace application

Extend the agentic system with useful, configurable **Workspace options** so the whole learning community can run new experiments and compare behavior. The instructor reviews proposed contributions before deciding whether to merge them. Participation is optional.

## Intended contribution scope

Focus on agentic capabilities and experiment options. Representative proposals include:

- **Guardrails:** add a selectable guardrail policy or provider and compare blocked/allowed behavior.
- **Model routing:** add a routing policy and compare quality, latency and cost on the same tasks.
- **Retrieval:** add a retrieval or reranking strategy and compare the returned evidence and answer quality.
- **Memory:** add a memory backend or retention strategy and compare what is stored, recalled and forgotten.

These are possible contributions, not features already supplied by this guide. Explain the capability, expose its configuration clearly, and implement the relevant backend or runtime behavior as well as its Workspace option. Include a comparison with the existing behavior and validation evidence. General Marketplace UI redesigns and unrelated commerce features are outside this contribution exercise.

The small Question starter walkthrough below teaches the branch, validation and pull-request mechanics. It is a UI-only example, not itself a new agentic capability. Use that workflow when proposing an agentic-system option from the scope above.

## The contribution sequence

1. Open the [course repository](https://github.com/smakam/agentic-systems). Sign in with your GitHub account. Reading or cloning a public repository does not grant write access; use your own fork to propose changes.
2. Select **Fork** to create a copy under your account. Clone **your fork**, then create a small feature branch. Learners do not need write access to the instructor's main branch.
3. Make one focused change. Explain the intended behavior, check the result locally, and include relevant evidence. A coding agent can help draft changes, but you review the diff and validate the behavior.
4. Commit and push the branch to **your fork**.
5. On the original repository, select **Pull requests → New pull request → compare across forks**. Set base repository to **smakam/agentic-systems**, base branch to **main**, head repository to **your fork**, and compare branch to **your feature branch**. Check that the diff contains only your intended change, then create the pull request.
6. The instructor reviews the proposal, may request changes, and decides whether to merge it. A pull request does not automatically enter the course application. No response time or acceptance is guaranteed.

A fork is the normal contribution path for learners without write access to the course repository. If the instructor has explicitly granted you collaborator write access, you can instead push a feature branch in the shared repository and open a pull request from it. Use course Q&A if you need help with the workflow.

### Example commands

Run these after creating your fork. Replace `YOUR-USER` with your GitHub username. Commands assume Git and GitHub authentication are configured.

```sh
git clone https://github.com/YOUR-USER/agentic-systems.git
cd agentic-systems
git switch -c add-question-starter
```

Follow [the setup guide](https://github.com/smakam/agentic-systems/blob/main/app/LOCAL-SETUP.md) for the environment. Keep credentials in your private local configuration.

## Worked example: add a Question starter Workspace option

**Goal:** add a dropdown in Support workspace → Workspace options. Selecting a question fills the existing question box. The learner can edit it and must press **Investigate** to run it. This example does not add a backend endpoint, change a runtime, alter permissions, or execute a business action.

This is example code for your branch, not a feature already shipped in the course application.

### 1. Create the component

Create `app/frontend/src/QuestionStarter.jsx`:

```jsx
import React from 'react';

const questions = [
  'Which sellers have unpaid funds, and how much?',
  'Why has Cedar & Co. not been paid for order-1?',
  'What is the current returns policy?',
];

export default function QuestionStarter({ disabled, onSelect }) {
  return (
    <label>
      Question starter
      <select
        aria-label="Question starter"
        value=""
        disabled={disabled}
        onChange={event => {
          if (event.target.value) onSelect(event.target.value);
        }}
      >
        <option value="">Choose a question</option>
        {questions.map(question => (
          <option key={question} value={question}>{question}</option>
        ))}
      </select>
    </label>
  );
}
```

The empty controlled value makes this a picker that returns to its placeholder after a selection. The question remains in the existing composer, which the Support component owns.

### 2. Connect it to the existing Support workspace

In `app/frontend/src/main.jsx`, add this import beside the other component imports:

```jsx
import QuestionStarter from './QuestionStarter.jsx';
```

Inside `Support`, locate `<h3>Workspace options</h3>` in the returned JSX. Immediately after that heading, before the existing Reset button, insert:

```jsx
<QuestionStarter
  disabled={pending || ragPreparing}
  onSelect={setQuestion}
/>
```

`Support` already defines `setQuestion`, `pending`, and `ragPreparing`. Reuse those values. The existing question submission path continues to handle runtime selection, requests, and authorization. The dropdown is a convenience for composing a question, not a backend experiment setting, so Reset to defaults does not need to persist or reset a new setting.

### 3. Validate your branch

Build the frontend from the repository root:

```sh
npm --prefix app/frontend ci
npm --prefix app/frontend run build
```

Run the application using the setup guide, then check:

- Sign in as a support-capable demo user and open **Support workspace**.
- The dropdown appears under **Workspace options**, with an accessible label.
- Select each starter. It fills the question box and makes no agent request until you press **Investigate**.
- Edit the populated question, then submit it through the existing button. Confirm the usual answer/error handling still works. Treat the response as a live result, not a fixed expected business answer.
- The picker is disabled while an investigation or RAG preparation is in progress.
- Existing runtime selection, Reset to defaults, and normal typed questions still work.
- Check the browser console and the build output. Capture a screenshot and record what you tested, including anything not tested.

A successful build checks compilation. It does not prove browser interaction, model access, or answer quality. Complete the manual checks before calling your contribution verified.

For a later option that changes agent behavior, trace the existing setting from frontend state to its API request, backend validation, runtime adapter, and relevant tests. Keep authorization and business rules enforced in the backend. Do not bypass them through a new UI control.

### 4. Submit the proposal

From your branch:

```sh
git diff --check
git diff -- app/frontend/src/main.jsx
git add app/frontend/src/QuestionStarter.jsx app/frontend/src/main.jsx
git diff --cached
git commit -m "Add a question starter Workspace option"
git push -u origin add-question-starter
```

Open the pull request using the sequence above. Suggested title: **Add a Question starter Workspace option**.

In the description include:

- **Problem and behavior:** picking a starter fills the composer and requires an explicit submission.
- **Scope:** one UI component plus its import and insertion in Support. No backend behavior change.
- **Validation:** build result, manual checks performed, screenshot, and limitations.
- **Costs:** identify any model calls or cloud resources used during testing.

Exclude secrets, private user data, databases, generated frontend bundles, dependency directories, and unrelated files. The instructor promotes accepted changes by reviewing and merging the pull request.

### 5. After review and merge

1. **Review:** the instructor checks the proposed behavior and validation, may request changes, and decides whether to accept it. Make requested changes on the same branch in your fork and push again; the existing pull request updates.
2. **Approval and merge:** approval records that the proposal is acceptable; it does not by itself merge the code. When ready, the instructor merges the pull request into the course repository’s **main** branch. The change then becomes part of the shared course source, rather than remaining only in your feature branch.
3. **Community access:** other learners can obtain the accepted improvement from the course repository. A merge does not automatically update anyone’s existing clone or running application, and it does not automatically deploy a cloud service.
4. **Update your copy:** in your fork on GitHub, use **Sync fork → Update branch** to bring its main branch up to date when GitHub can do so without conflicts. Save or commit local work before switching branches. Pull the updated main branch into your local clone, then follow the [Local Setup guide](../app/LOCAL-SETUP.md) to rebuild or restart the affected services and verify the new behavior. Ask in course Q&A if synchronization reports conflicts.

The contribution path is: **your fork’s feature branch → pull request → instructor review → merge into course main → learners update and validate their copies**. Acceptance and deployment remain separate decisions.

## References

- [GitHub: Forks and access requirements](https://docs.github.com/en/pull-requests/reference/forks)
- [GitHub: Creating a pull request from a fork](https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/creating-a-pull-request-from-a-fork)
