"""Graph Admin Studio shared domain packages.

This package intentionally contains *only* reusable domain logic that can be
imported by both:
- interactive UI backends (Flask/FastAPI), and
- standalone scripts (automation, local tooling).

It should not import UI modules.
"""

