# 🛡️ VAJRA – Shakti Kavach

### Prototype Platform for Secure Incident Capture, Evidence Integrity & Emergency Response

[![iDEX – Defence Innovation](https://img.shields.io/badge/iDEX-Defence%20Innovation-blue)]
[![Status](https://img.shields.io/badge/Status-Prototype-orange)]
[![Python](https://img.shields.io/badge/Python-3.8+-green)]
[![Flask](https://img.shields.io/badge/Backend-Flask-red)]
[![License](https://img.shields.io/badge/License-MIT-lightgrey)]

> **VAJRA – Shakti Kavach** is a **prototype defence-oriented safety and incident-support system** designed to enable **secure incident capture, evidence integrity, and response visibility** in controlled and high-risk environments.

> ⚠️ This project is a **pilot-stage prototype**, intended for evaluation under government and defence innovation programs such as **iDEX (MoD, India)**.

---

## 🎯 Problem Context

Across defence establishments, internal security units, and critical infrastructure environments, incident handling often faces:

- Delayed acknowledgment of incidents  
- Risk of evidence loss or tampering  
- Limited audit visibility across response layers  
- Inadequate tooling for rapid, privacy-respecting incident capture  

VAJRA – Shakti Kavach focuses on **process integrity and response enablement**, not enforcement or adjudication.

---

## 🧩 System Overview

The platform follows a **modular architecture**, consisting of **one mobile/edge component and a secure backend**, with future governance tooling planned for pilot deployments.

---

### 1️⃣ Shakti Kavach – Mobile / Edge Application (Prototype)

A lightweight incident-capture application intended for **controlled pilots**.

**Capabilities**
- Manual emergency (SOS) trigger
- Contextual data capture (audio / sensor-assisted)
- Local encryption before transmission
- Operable in low or intermittent connectivity

**Explicitly Out of Scope**
- No FIR registration  
- No automated accusations  
- No public disclosure  
- No autonomous law enforcement actions  

---

### 2️⃣ VAJRA Backend – Secure Ingest & Logging (Prototype)

A backend service responsible for **receiving, time-stamping, and logging incident data**.

**Core Functions**
- Secure ingest API
- Cryptographic hashing for evidence integrity
- Append-only logging model
- Role-based admin access (development / pilot use)

> Current implementation demonstrates system flow using a **local development backend (localhost)**.

---

### 3️⃣ Governance & Audit View (Planned – Pilot Phase)

A future component designed for **authorised supervisory and audit visibility**.

**Purpose**
- Monitor acknowledgment timelines
- Enable delay visibility
- Support post-incident audits (metadata-first)

---

## 🔐 Security & Integrity Principles

- End-to-end encryption (prototype-grade)
- Cryptographic hashing of captured evidence
- No delete or overwrite operations on evidence logs
- Role-based access control
- Human-in-the-loop at all decision points

> The system is designed to **support lawful processes**, not replace them.

---

## ⏱️ Delay Visibility Model (Conceptual)

The platform introduces **time-based visibility**, not punitive escalation.

**Indicative Pilot Model**
- 0–2 hours: Local acknowledgment expected  
- 2–24 hours: Supervisory visibility  
- 24–72 hours: Audit metadata availability  
- 72–120 hours: Statutory review report (if required)  

✔ No automatic penalties  
✔ No public exposure  
✔ No bypass of courts or command authority  

---

## 🧪 Current Status

✅ **Implemented**
- Shakti Kavach light mobile prototype
- Emergency trigger and data capture
- Backend receipt via admin panel

🛠️ **Planned with Grant / Pilot Funding**
- Secure production backend
- Persistent evidence vault
- Governance dashboard
- Controlled defence or security pilot

---

## 🗺️ Proposed Roadmap

**Phase 1 – Pilot Hardening**
- Backend security upgrades
- Persistent storage & audit logs

**Phase 2 – Controlled Deployment**
- Limited pilot with authorised units
- Independent evaluation and feedback

**Phase 3 – Review & Alignment**
- Compliance and security audit
- Policy and scale feasibility assessment

---

## 🏗️ High-Level Architecture

