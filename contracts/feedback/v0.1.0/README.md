# OpenRGD Feedback Contracts v0.1.0 — CANDIDATE

**Maturity:** `candidate`; `normative: false`; **not an accepted standard**, installable module, live event bus, or new Canonical RGD domain.

Purpose: define a minimal, modality-neutral contract for **what the robot wants to communicate**, separately from **how a device communicates it**. The same intent may be rendered as Visual Feedback (LED/display/ambient light) and Audio Feedback (earcon/chime), by independent modules with independent device owners.

## Separation of concerns

```text
Voice / Vision / IMU / Operations / operator
                  |
      producer-native events
                  |
      explicit normalized Signal
                  |
      reviewed mapping & arbitration
                  |
     semantic Cue Intent + short TTL
                  |
        independent per-modality policies
                  |
       Visual service      Audio service (future)
         |                       |
  scene/zone renderer      earcon/mixer policy
         |                       |
  PERIPH-backed adapter    host audio output owner
         |                       |
  LEDs/display/room light  approved speaker(s)
                  |
        Delivery Reports (driver acknowledgement != sensor observation)
```

Feedback does **not** belong to Somatic Runtime's 1 kHz loop and never grants actuator motion. All feedback effects are best-effort and optional.

## Contracts

| File | Producer | Consumer | Purpose |
|---|---|---|---|
| `schemas/feedback-signal.v0.1.schema.json` | Explicit event adapter | Feedback router | Source/provenance/time-labeled event; may map from existing Voice/Console schemas |
| `schemas/feedback-cue.v0.1.schema.json` | Feedback policy engine | Per-modality renderer | Semantic cue, priority, TTL and requested modalities; **no** effect parameters |
| `schemas/feedback-capabilities.v0.1.schema.json` | Peripheral owner/adapter | Renderer/operator | Logical zone, effect support, operator provenance and local comfort limits; **no** hardware address |
| `schemas/feedback-delivery.v0.1.schema.json` | Independent output adapter | Console/Feedback observations | Command/driver-stage status, always `physical_output_observed=false` in this candidate |

See `examples/feedback-flow.synthetic.json`. All examples are **synthetic**. An example containing `driver_ack` demonstrates the report *shape*, not a new physical test.

`STATUS.json` states current maturity and promotion gates. `RFC.md` explains design tradeoffs and open questions.

## Key compatibility decisions (candidate)

- Do **not** replace existing `org.openrgd.voice.lifecycle.v0.1-candidate`, `openrgd.visual.voice-event.v0.1-candidate`, `console.module.v1` or Console's operational event contract in place. Write explicit bridge adapters and test them.
- A Source Event is not necessarily a sensory observation; browser `playing` and `paplay` process start are producer **reports**. Avoid invented `physical_audio_observed` or verified perception labels.
- A Cue contains **semantics**, e.g. `conversation.speaking`, not `#00FF46`, `speaker_bose`, `beep.wav` or BLE MAC. Visual and Audio modules own those mappings.
- `modalities: ["visual", "audio"]` means independently *attempt* permitted outputs; failure of one must not block the other or delay speech.
- Each output zone must have **one active owner**; source modules and browser UIs do not pair or control peripherals directly. Align with the evolving PERIPH service rather than creating duplicate hardware discovery.
- `presentation` distinguishes a one-shot cue (e.g. a brief audio earcon) from a leased state (e.g. the robot listening or speaking). `ttl_ms` is a **finite lease**; long-lived states require renewal or explicit follow-up events after arbitration is implemented. Never leave stale speech/error visual states indefinitely.
- `priority` resolves output conflicts only under an independently reviewed policy; it is never a safety priority or emergency-stop permission.
- Hardware capability catalogs do not prove that a device is connected. Status/freshness/verification remain separate.
- `physical_output_observed=false` means there is no independent light/sound measurement. For example, Visual v0.3 `applied` maps only to driver write/ack and **must not** be promoted to measured emitted light.

## Outputs we may eventually support

**Visual:** single indicator LEDs, RGB rings, addressable pixel strips, light bars, LED matrices/eyes, OLED/TFT/e-ink status surfaces, diffuse illumination, projector graphics, smart-room lighting and DMX/Art-Net/sACN show cues. Effects, rate and power are adapter-specific; many are currently unsupported.

**Audio:** short earcons/chimes, nonverbal alerts and ambient/acoustic responses, spatial cues where supported. Voice synthesis/conversation remains the responsibility of Voice Studio; audio feedback must not independently read microphones, perform STT or create a second TTS engine. Audible output needs session mixing/ducking policy, silence mode, bounded volume and device ownership.

**Future modalities:** haptic/thermal feedback would require a separately reviewed contract revision; they are intentionally **not** in the v0.1 enum.

## Scope limitations / next review

This directory is design material only. No transport, event arbiter, host daemon, peripheral registry integration, UI control, remote room lights, audio module or automatic installation is delivered. Audio output-device selection remains outside this contract.

Review with PERIPH-0.2, Voice Studio, Visual Studio and Console owners before field promotion. A shared contract must not loosen the non-actuating security boundaries or claim hardware/Chronograph evidence unavailable to it.

Run optional schema and reference-flow conformance checks (using Python `jsonschema`) via:

```bash
python3 -m pip install 'jsonschema==4.23.0'  # optional candidate checker only
python3 -m unittest discover -s contracts/feedback/v0.1.0/tests -p 'check_*.py' -v
```

See `GOVERNANCE.md` for human acceptance; no candidate becomes normative merely by merging.
