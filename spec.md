# System specification

## Intro
This repo will eventually contain a specification for building scalable systems composed of smaller components.

## Component
A small independent part that implement one or more capabilites.

- Each component can depend on zero or more dependant components.

## Data models

Each component might own one or more data sets. Data can be external and internal. Use of external data shall be tracked and rexported properties as well.

## Risk, Requirements and Tests
Capabilities of a component are specified with requirements, each requirement needs proof. Either by one or more tests or by other means.

Risks of each components shall be listed. Each risk shall be mitigated by one or more requirements. Each of these requirements shell be verified by tests or proof.