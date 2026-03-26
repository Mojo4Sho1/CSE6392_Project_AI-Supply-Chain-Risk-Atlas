PYTHON    := /Applications/MiniConda/miniconda3/envs/ai-supply-chain-risk-atlas/bin/python
INPUT     := data/models.csv
OUTROOT   := .
TIMESTAMP ?= $(shell date -u +"%Y-%m-%dT%H:%M:%SZ")
MANIFEST_STAMP := manifests/.stage_complete
OSV_STAMP      := osv/.stage_complete
GRAPH_FILE     := graphs/global.graphml
REPORT_STAMP   := reports/.stage_complete

.PHONY: test ingest scan graph report all dashboard validate clean

test:
	$(PYTHON) -m pytest -q

all: report

dashboard:
	$(PYTHON) scripts/run_dashboard.py \
	  --graph $(GRAPH_FILE) \
	  --summary reports/summary.json \
	  --table reports/summary.csv \
	  --host 127.0.0.1 \
	  --port 8050

validate:
	$(PYTHON) scripts/ingest_repo_artifacts.py --help >/dev/null
	$(PYTHON) scripts/run_osv_scan.py --help >/dev/null
	$(PYTHON) scripts/build_risk_graph.py --help >/dev/null
	$(PYTHON) scripts/generate_atlas_reports.py --help >/dev/null
	$(PYTHON) scripts/run_dashboard.py --help >/dev/null
	$(MAKE) all
	$(MAKE) test
	test -f graphs/global.graphml
	test -f reports/summary.json
	test -f reports/summary.csv
	test -f figures/reused_vulnerable_packages.png
	test -f figures/impacted_model_count_distribution.png
	find manifests -mindepth 2 -maxdepth 2 -name manifest_index.json | grep -q .
	find osv -mindepth 2 -maxdepth 2 -name normalized.json | grep -q .
	if rg -n "OPEN_DECISION" docs/specs README.md docs/handoff --glob '!docs/specs/testing-and-validation.md'; then exit 1; fi

ingest: $(MANIFEST_STAMP)

$(MANIFEST_STAMP): data/models.csv scripts/ingest_repo_artifacts.py
	@if [ ! -e "$@" ] && [ -d manifests ] && find manifests -mindepth 2 -name manifest_index.json | grep -q .; then \
	  mkdir -p $(dir $@) && touch "$@"; \
	else \
	  $(PYTHON) scripts/ingest_repo_artifacts.py \
	    --input $(INPUT) \
	    --output-root $(OUTROOT) \
	    --snapshot-timestamp "$(TIMESTAMP)" && \
	  touch "$@"; \
	fi

scan: $(OSV_STAMP)

$(OSV_STAMP): $(MANIFEST_STAMP) scripts/run_osv_scan.py
	@if [ ! -e "$@" ] && [ -d osv ] && find osv -mindepth 2 -name normalized.json | grep -q .; then \
	  mkdir -p $(dir $@) && touch "$@"; \
	else \
	  $(PYTHON) scripts/run_osv_scan.py \
	    --input manifests \
	    --output-root $(OUTROOT) \
	    --snapshot-timestamp "$(TIMESTAMP)" && \
	  touch "$@"; \
	fi

graph: $(GRAPH_FILE)

$(GRAPH_FILE): $(OSV_STAMP) $(wildcard osv/*/normalized.json) scripts/build_risk_graph.py
	$(PYTHON) scripts/build_risk_graph.py \
	  --input osv \
	  --output-root $(OUTROOT) \
	  --snapshot-timestamp "$(TIMESTAMP)"

report: $(REPORT_STAMP)

$(REPORT_STAMP): $(GRAPH_FILE) scripts/generate_atlas_reports.py scripts/_utils/report_build.py
	$(PYTHON) scripts/generate_atlas_reports.py \
	  --input $(GRAPH_FILE) \
	  --output-root $(OUTROOT) \
	  --snapshot-timestamp "$(TIMESTAMP)"
	@mkdir -p $(dir $@) && touch "$@"

clean:
	rm -rf manifests/ osv/ graphs/ reports/ figures/
