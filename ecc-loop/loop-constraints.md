# ECC Loop — Constraints (Machine-Readable Safety)

DO NOT MODIFY:
.env
.env.*
**/secrets/**
**/credentials/**
**/*_key*
**/*_secret*
**/migrations/**
auth/**
payments/**

HUMAN GATE REQUIRED:
- Changes touching >10 files
- Dependency version changes
- Any file matching denylist
- Third failed attempt on same item
- Security/auth related changes
