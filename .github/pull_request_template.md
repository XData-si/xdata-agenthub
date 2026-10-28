## Summary

## Type
- [ ] New skill
- [ ] Skill change
- [ ] CLI / scripts
- [ ] Documentation / other

## For skills
- [ ] `skills/<id>/SKILL.md` with a description that says what the skill does **and when to use it**
- [ ] Procedure, example fixture, acceptance checks with a negative case, and a **Safety** section
- [ ] Instructions only: no scripts, binaries, download links or hidden content
- [ ] Catalog entry, `docs/CATALOG.md` and marketplace bundle updated; `python3 scripts/update_digests.py` run
- [ ] `python3 scripts/skill_security_check.py <id>` passes locally
- [ ] I did not add or change seals (maintainers grant them after review)

Every skill is security-reviewed before distribution: the required security gate and an advisory AI review run on this
pull request, followed by maintainer review. See [CONTRIBUTING.md](../CONTRIBUTING.md).

## Tests performed

## License and provenance of added content

## Security and compatibility considerations

## Checklist
- [ ] No secrets or third-party content without redistribution rights
- [ ] Tests and documentation updated
- [ ] Claims about support are verified
