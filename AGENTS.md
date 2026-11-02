# Persistent model and delegation preference

For work in this repository, follow the user's explicit model assignment:

- Use **GPT-6.1 Sol** with **high** reasoning for overall ownership: scope, implementation method, architecture, integration, and final acceptance.
- Delegate concrete implementation and code changes only to **GPT-6 Luna** with **medium** reasoning.
- Do not assign this repository's work to other models or use other reasoning-effort levels for its agents or delegated tasks.
- Keep final verification and acceptance with GPT-6.1 Sol (high); implementation agents report changes and checks for independent review.

These are persistent user preferences and take precedence over default model/delegation choices for this project.

## Desktop application synchronization

- After every code change, automatically synchronize the desktop application with the updated source, including any required hot reload or restart.
- Verify that the desktop application is running and serving the current source/version, and report the synchronization check in progress updates.
- Before final delivery, ensure the desktop application has loaded the final version and verify it again.
