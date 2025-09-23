PY=./.venv/bin/python
CLI=./.venv/bin/python -m prop.cli
BASE?=http://127.0.0.1:8000

.PHONY: demo
## demo: demonstrate intake then score using sample files (requires server running at $(BASE))
demo:
	$(CLI) intake examples/pws_sample.md > /tmp/opp_intake.json
	cat /tmp/opp_intake.json | jq '.'
	cp examples/opportunity_sample.json /tmp/opp_score.json
	$(CLI) score --json /tmp/opp_score.json | jq '.'
.PHONY: cover
## cover: generate sample cover.docx from examples/cover_sample.json
cover:
	$(CLI) cover examples/cover_sample.json -o cover.docx

