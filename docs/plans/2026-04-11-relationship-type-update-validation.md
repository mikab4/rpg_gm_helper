# Relationship Type Update Validation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Reject invalid relationship type update direction combinations explicitly instead of silently normalizing them.

**Architecture:** Validate payload-only contradictions in the Pydantic update schema, then validate the effective post-update state in the service because partial PATCH requests do not contain enough context for schema validation alone. Keep the database check constraint as the final backstop.

**Tech Stack:** FastAPI, Pydantic, SQLAlchemy, pytest, Ruff

---
