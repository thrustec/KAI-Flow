# client/app/components/ — React Components

## Folder Purpose
All reusable and feature UI components. The canvas + node components here are the visual half of
the AI workflow system.

## What This Folder Contains / File-by-File Explanation

### Root components
`AuthGuard.tsx` / `PublicOnlyGuard.tsx` (route protection), `KeycloakLoginButton.tsx`,
`KaiChatWidget.tsx` (embeds the `@kaifusion/widget` package in-app), `DashboardChart.tsx`
(Recharts), `BackgroundGradient.tsx`, `Loading.tsx`.

### `canvas/` — the workflow editor
- `FlowCanvas.tsx` — **central component**: XYFlow state (nodes/edges), drag-drop from sidebar,
  save/autosave, undo/redo (`lib/useWorkflowHistory.ts`), execution triggering with node status
  coloring, unsaved-changes handling, keyboard shortcuts, log panel + chat integration.
- `ReactFlowCanvas.tsx` — the `<ReactFlow>` wrapper (viewport, zoom, connections).
- `ChatComponent.tsx` — chat panel for testing workflows; `ChatHistorySidebar.tsx` — past
  sessions.
- `LogPanel.tsx` — live log terminal (backend `/api/v1/logs` streaming).
- `NodeContextMenu.tsx` — right-click menu; `ErrorDisplayComponent.tsx` — execution errors.

### `node/` — node rendering & configuration
- `GenericNode.tsx` / `GenericVisual.tsx` — renders any node from backend `NodeMetadata`.
- `GenericNodeForm.tsx` — builds the configuration form from metadata.
- `fields/` — one component per `NodePropertyType`: `NodeText`, `NodeTextArea`, `NodeSelect`,
  `NodeCredentialSelect`, `NodeCodeEditor` (+ `monaco/`), `NodeJsonEditor`, `NodeNumber`,
  `NodePassword`, `NodeCheckbox`, `NodeRange`, `NodeDateTime`, `NodeSessionId`,
  `NodeReadonlyText`, `NodeTitle`, `FieldLabel`.
- `StartNode.tsx`, `EndNode.tsx`, `StickyNoteNode.tsx` — special-cased nodes; `types.ts`,
  `index.ts`.

### Other feature folders
- `modals/` — `WorkflowEditModal`, `WorkflowExportModal`, `WidgetExportModal` (embed-code
  generator), `DataViewModal`, `AutoSaveSettingsModal`, `SmartSuggestionsSettingsModal`,
  `UnsavedChangesModal`, `DeleteConfirmationModal`, `ErrorWorkflowModal`.
- `credentials/` — `DynamicCredentialForm`, `CredentialSelector`, `CredentialCard`,
  `CredentialWorkflowUsage` (deletion protection UI), `ServiceSelectionModal`,
  `credentialPayload.ts`.
- `common/` — `Navbar`, `Sidebar` (node palette), `CustomEdge`, `NeonHandle`, `JSONEditor`,
  `DraggableNode`, `RecommendedNodes`, `TabNavigation`, `ThemeToggle`, `ErrorBoundary`,
  `FullscreenNodeModal`, `PinButton`/`PinnedItemsSection`, `ChatBubble`, `DataDisplayModes`,
  `ToggleSwitch`.
- `tutorial/` — guided tutorial (`TutorialLauncher`, `TutorialWorkflowGuide`, `TutorialButton`),
  data in `app/data/tutorialWorkflows.ts`.
- `external/` — `ExternalWorkflowViewer`, `ExternalWorkflowChat` (imported external workflows).
- `dashboard/` — `DashboardSidebar`.

## Important Files
`canvas/FlowCanvas.tsx`, `node/GenericNodeForm.tsx`, `common/Sidebar.tsx`.

## Relationship With Other Folders
- State via `app/stores/`; HTTP via `app/services/`; hooks/config from `app/lib/`; node metadata
  comes from backend `app/api/nodes.py` (defined in `backend/app/nodes/`).

## How This Folder Fits Into the AI Workflow
The canvas produces/edits the `flow_data` graph; `GenericNodeForm` renders each node's
configuration from backend metadata — so backend node changes appear here without frontend code
changes (unless a new `NodePropertyType` is introduced, which needs a new field component).

## Developer Notes
- New backend field type ⇒ add a component under `node/fields/` and map it in `fields/index.tsx`.
- Follow the store→service layering; components should not call axios directly.

## Things to Be Careful About
- `FlowCanvas.tsx` is very large and central — small changes can affect saving, undo/redo, and
  execution status rendering; test the canvas flow manually after edits.
- Node status coloring depends on SSE event shapes from the backend; keep event parsing in sync
  with `backend/app/api/workflows.py`.

## Related Documentation Files
[../../CLIENT.md](../../CLIENT.md) · [../stores/STORES.md](../stores/STORES.md) ·
[../services/SERVICES.md](../services/SERVICES.md) ·
[../../../backend/app/nodes/NODES.md](../../../backend/app/nodes/NODES.md)
