"""WBC: capability-layered RL package for G1 humanoid loco-manipulation.

The top-level package is intentionally lightweight.  Import task registries
explicitly with ``import WBC.tasks`` after Isaac Lab / AppLauncher is ready.
This keeps utility modules such as ``WBC.eval`` importable before ``pxr`` is
available.
"""

__all__: list[str] = []
