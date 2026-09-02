# Glossario OpenRGD

## Aion

Payload/state isotope associated with a Chronon in the RGD-Physics lineage. It is distinct from the `AION` temporal layer name used by Robot Chronograf; context and capitalization matter.

## AION

A temporal/relational layer name in the Chronograf lineage and, in some historical discussions, a memory/identity namespace. The reconciliation avoids treating every occurrence as the same object.

## ActionIntent

Model-agnostic semantic description of an action request. It expresses what is requested without embedding servo IDs, transport frames or hardware-specific commands.

## Body Adapter

Component that translates an approved hardware-agnostic capability plan into commands for a specific body, bus, simulator or robotic framework.

## Canonical Core

The minimal set of repository-level authorities, contracts and invariants needed to keep the ecosystem coherent. It is not a claim that every runtime component belongs in one monolith.

## CapabilityPlan

Hardware-agnostic plan emitted by the Somatic Translator. It contains declared capability steps, parameters, expected effects and execution constraints.

## Candidate

A recovered or converged artifact under review. Candidate material is not stable or normative merely because it is versioned in the canonical repository.

## Chronograf

The temporal subsystem responsible for clock domains, TimeAtoms, uncertainty, channels and anchor issuance/resolution.

## Chronon

Immutable causal/history envelope in the RGD-Physics lineage. In the convergence candidate, Chronons are canonical evidence from which memory projections are built.

## CognitionProposal

Structured output from an LLM, VLM, VLA, planner, world model or deterministic cognition provider. It can carry ActionIntent, AION context, optional HyperAion references and Chronon evidence references.

## DecisionTrace

Structured audit artifact recording policy layer, outcome, rule references, evidence and commitments. It deliberately excludes private chain-of-thought.

## Domain

One semantic layer of the OpenRGD graph: Foundation, Operation, Agency, Volition, Evolution or Ether. `00_core` coordinates these domains.

## Ethos Packet

Separate forensic/ethical artifact from the RGD-Ethics lineage. The current candidate contract links it to Chronons and DecisionTrace without declaring it to be a Chronon.

## HyperAion512

Candidate 512-dimensional cognitive representation recovered from the HyperKernel lineage. It can support soft resonance or ranking but does not grant permission to actuate.

## Manifest

Top-level descriptor declaring a bundle identifier, target standard version, ownership and domain maturity.

## OpenRGD

Robot Graph Definition: the open semantic standard and repository ecosystem for describing cognitive embodiment.

## Operation Safety Gate

Hard runtime boundary that evaluates an intended capability plan against operational, safety and constitutional constraints before execution.

## Projection

Derived memory or index such as an episode, fact, skill, summary or embedding. Projections can be rebuilt; they do not replace canonical historical evidence.

## Semantic Graph

Interconnected, machine-readable representation of a robot's body, operation, agency, values, lifecycle and collective context.

## Somatic Translator

Hardware-agnostic boundary that converts approved action semantics into a CapabilityPlan. It stops before device-specific actuation.

## Synapse

Interoperability layer translating OpenRGD semantics into or from external formats and runtimes such as URDF, USD, ROS 2 or Isaac-oriented configurations.

## TimeAtom

Measured temporal coordinate with resolution, timescale, uncertainty and reference evidence, interpreted within a declared clock domain.

## Toolchain `rgd`

Installable Python CLI used to initialize, inspect, compile, import, export and boot OpenRGD bundles. Its package version is independent from the standard version.
