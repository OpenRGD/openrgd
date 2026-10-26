# Draft RFC — Multimodal Feedback Signals and Cue Intents

**RFC status:** DRAFT / candidate for review, not accepted.  
**Date:** 2026-10-26.  
**Owner:** OpenRGD cross-component contracts, under human maintainer governance.

## Problem

Today Paky-01's tested Miracles.Star RGB ring receives Voice Studio lifecycle events over the Visual Feedback Unix socket. Visual Effects Studio already has a separate draft mapping engine and Console preview. A future independent Audio Feedback service should react to the same **semantic situation** without copying Voice-specific event names, hardware addresses, LED colors or mixing/audio policy.

If every feedback implementation invents its own event and priority semantics, concurrent modalities will disagree about what the robot is doing. Conversely, if a shared contract mandates BLE/ALSA/Wi-Fi control, it improperly merges hardware ownership and risks breaking Voice, PERIPH and Somatic boundaries.

## Proposed decision (for review only)

Use a four-part, versioned candidate model:

1. **FeedbackSignal** — typed normalized information from a source adapter, with unique signal ID, robot instance, event source, session/sequence (if available), and explicit provenance/time quality. This stage cannot assert output success.
2. **FeedbackCue** — policy-engine intent explaining *what should be communicated*: semantic `cue_key` (e.g. `conversation.speaking`, `robot.welcome`), category, best-effort modality set, bounded priority and finite TTL. No output protocol, animation, WAV filename or mic/speaker ID is in this object.
3. **FeedbackOutputCapabilities** — one *owner-declared* logical peripheral/zone, modality, effect IDs and installation-enforced limits. A declaration is not proof of device availability. PERIPH is the intended future source of physical device lifecycle and capability bindings; this candidate does not claim its current API.
4. **FeedbackDeliveryReport** — output progress (`requested/queued/sent/driver_ack/failed/expired/dropped/unavailable`) per zone and modality, explicitly separating transport acknowledgement from physical verification. In v0.1, `physical_output_observed` is always false.

There is **one effect writer per physical device or output zone**. Feedback source modules never access a shared peripheral directly.

## Concrete portable example

```text
Source: Voice `playback.started` (from actual playback callback)
          │
          ▼
FeedbackSignal (reported lifecycle, non-authoritative)
          │
          ▼
FeedbackCue (`conversation.speaking`, priority 50, TTL lease 60s)
          │
          ├── Visual policy: `speaking` scene → face-ring green
          └── Audio policy: none (do not overlay a chime while voice speaks)
```

By contrast, an **explicit operator greeting** may request both `visual` and `audio`, creating an RGB scene and a short earcon. If the speaker adapter does not exist, `unavailable` is a legitimate output report and the visual scene is unaffected.

## Logical peripheral taxonomy

| Logical visual type | Candidate effects | Likely physical adapter owner | Boundary |
|---|---|---|---|
| Mono status LED / optocoupled indicator | on/off, level | PERIPH-bound GPIO/Pico | No arbitrary high-voltage wiring |
| RGB ring / bar | solid, transition, pulse | Existing BLE ring; future USB-serial adapter | Only solid color and brightness have Paky-01 physical evidence today |
| Addressable pixel strip / segmented ring | chase, progress, orientation, wave | Pixel adapter on microcontroller | No model assumptions about pixel count, timing or current |
| LED matrix / expressive eyes | pixels, icons, expressions | Display/Matrix adapter | Face images and private content require operator policy |
| OLED/TFT/e-ink screen | text, icons, progress, low-rate status | Display service | E-ink is not a high-frequency animation backend |
| Diffuse/ambient room light | solid, fades, scenes | Authorized host-side room-light gateway | No browser pairing, external LAN exposure or automatic device discovery |
| Projection / show lighting | bounded 2D projection or DMX scenes | Specialized output controller | Consent, privacy, brightness, public-environment limits |

Each adapter advertises only tested capabilities. The contract does not promise that all kinds are suitable for Paky-01.

**Audio candidate output classes:** short WAV/PCM earcons, status chimes, ambient loops and spatial notification cues. Audio Feedback owns **notification sound semantics**, not STT/TTS, microphone selection or the voice/persona default. A host user-session audio output owner coordinates with Voice Studio so an alert cannot arbitrarily mask speech or create microphone echo loops.

## Arbitration and ergonomics (required before runtime)

The v0.1 schemas capture `priority` and `ttl_ms` but **do not implement scheduling**. A later arbiter must define:

- Preemption across sources and modalities, with stable source-specific leases and a bounded default fallback.
- Explicit `start/refresh/end` cue lifecycle for long speech/cognition states (avoid stale permanent green or purple).
- Per-zone occupancy and output ownership: one writer per zone, no simultaneous independent BLE writers.
- Coalescing/sequence/replay handling across browser HTML audio and backend `paplay` activity.
- Operator preference profiles: quiet hours, sound mute, reduced motion, brightness cap, photosensitivity protection; no high-rate flashing without independent review.
- Independent delivery: audio absent does not block visual; visual offline does not block speech. Never treat a cue as E-stop, collision warning guarantee or readiness certification.
- Safe output limits established through real hardware/installation review, not inferred from a percent field. A volume percentage is not an acoustic SPL measurement.
- Local-first operations and explicit consent/authentication for remote lamps or environment effects.
- Failure handling: driver disconnected, stale update, missing physical confirmation and unknown robot instance must not be silently reported as success.

## Compatibility and migration plan

| Existing contract / subsystem | Candidate adapter treatment | Do not do |
|---|---|---|
| `org.openrgd.voice.lifecycle.v0.1-candidate` | Map native `evidence_kind/state` into normalized FeedbackSignal and semantic cue; preserve original source event and session/sequence. | Rewrite or re-version the Voice contract implicitly. |
| `openrgd.visual.voice-event.v0.1-candidate` | Continue serving existing v0.3 BLE daemon; a future bridge consumes FeedbackCue and submits local `set_state` if supported. | Remove/replace the working socket without physical regression test. |
| Visual Effects Studio preview profile | Keep Visual-specific `scenes`, `color`, `brightness`, logical zones and capability checks in Visual module. | Put RGB effect values into shared CueIntent. |
| Console operational events | Read-only projection of FeedbackDeliveryReports, with clear evidence/clock domain and stale freshness. | Promote driver ack to source-certified light/sound observation. |
| PERIPH-0.2 | Align discovery, pairing, lifecycle, ownership and peripheral IDs before binding actual devices. | Make a duplicate BLE or peripheral manager inside Feedback. |
| Audio Feedback future | Map CueIntent to independent earcon/mixer policies, and publish optional delivery reports. | Duplicate Voice TTS/STT, open audio devices from browser or compromise Voice real-time playback. |

Feedback contracts are a **cross-component candidate**, not a new `spec/` domain and not a Somatic ActionIntent. The current canonical Core runtime boundary remains non-actuating.

## Open questions requiring review

1. Will feedback lifecycle be a separate small `rgd-feedback` implementation, or an interface hosted in the peripheral/event orchestrator? The **contract** stays in `OpenRGD/openrgd`, independently of that choice.
2. Should `priority` be global or scoped by zone/renderer when visual and audio have different user preferences?
3. What is the stable mapping between local `robot_id` in Console, `robot_instance_id` in Voice and any future canonical robot identity?
4. What verified permission contract authorizes remote/external lighting, speaker selection and user-facing privacy choices?
5. When PERIPH-0.2 publishes its actual descriptors, how will IDs and capabilities be imported without inventing virtual hardware?
6. Do future emotion/intention cues need structured semantic tags or should they remain stable `cue_key` names until one full multimodal physical experiment is recorded?

## Acceptance / exit gates

Do **not** promote while there is no implemented producer → adapter → policy → two independent renderers flow. Before acceptance require conformance tests for all four schema types, negative fixtures, source-provenance rules, TTL/priority arbitration tests, scoped permissions, hardware-disconnect fallbacks, observational truthfulness, human RFC acceptance and a reviewed field canary. Until then the package remains `candidate`, `normative:false`.
